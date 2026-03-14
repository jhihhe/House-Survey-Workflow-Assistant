
import ExcelJS from 'exceljs';
import path from 'path';
import fs from 'fs-extra';
import { ShootInfo, parseShootLine } from './folder-parser';

// --- Python Logic Port ---

function norm(v: any): string {
    if (v === null || v === undefined) return "";
    let s = "";
    if (v instanceof Date) {
        s = `${v.getMonth() + 1}月${v.getDate()}日`;
    } else if (typeof v === 'object' && v.richText) {
        s = v.richText.map((t: any) => t.text).join('');
    } else {
        s = String(v);
    }
    // Aggressive cleanup: remove all whitespace including NBSP
    return s.replace(/[\s\u00A0\u3000]+/g, "").trim();
}

function deepClone<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj));
}

function findHeaderRowAndMap(sheet: ExcelJS.Worksheet) {
    const wanted: Record<string, string[]> = {
        "photographer": ["摄影师"],
        "name": ["接单人", "经办人", "经纪人"],
        "hs": ["原房源号", "房源号", "原房源编号"],
        "store": ["接单人所属门店", "所属门店"],
        "address": ["房源地址", "小区", "楼盘名称", "楼盘", "房勘社区"],
        "room": ["房号", "房源房号", "门牌号"],
        "direction": ["入户门", "朝向"],
        "shoot_date": ["拍摄时间", "拍摄日期"],
        "seq": ["序号"],
        "monthly_count": ["当月套数"],
    };

    let bestRow = 0;
    let bestScore = -1;
    let bestMap: Record<string, number> = {};

    const maxScanRows = Math.min(20, sheet.rowCount);

    for (let r = 1; r <= maxScanRows; r++) {
        const row = sheet.getRow(r);
        const rowMap: Record<string, number> = {};
        let score = 0;

        // Iterate all cells in row (up to max column)
        const maxCol = sheet.columnCount || 20; 
        for (let c = 1; c <= maxCol; c++) {
            const cell = row.getCell(c);
            const v = norm(cell.text || cell.value); // Handle Rich Text
            if (!v) continue;

            for (const key in wanted) {
                // Python logic: if key in row_map: continue
                if (rowMap[key]) continue;

                const aliases = wanted[key];
                for (const alias of aliases) {
                    if (v.includes(alias)) {
                        rowMap[key] = c;
                        score++;
                        break;
                    }
                }
            }
        }

        if (score > bestScore) {
            bestScore = score;
            bestRow = r;
            bestMap = rowMap;
        }
    }

    return { headerRow: bestRow, headerMap: bestMap, headerScore: bestScore };
}

function findHsColumn(sheet: ExcelJS.Worksheet, headerRow: number, headerMap: Record<string, number>): number {
    if (headerMap['hs']) return headerMap['hs'];

    const maxCol = sheet.columnCount || 20;
    
    // Scan header row
    for (let c = 1; c <= maxCol; c++) {
        const v = norm(sheet.getCell(headerRow, c).text || sheet.getCell(headerRow, c).value);
        if (v && v.includes("HS")) return c;
    }

    // Scan down 50 rows
    const scanTo = Math.min(sheet.rowCount, headerRow + 50);
    for (let c = 1; c <= maxCol; c++) {
        for (let r = headerRow + 1; r <= scanTo; r++) {
            const v = norm(sheet.getCell(r, c).text || sheet.getCell(r, c).value);
            if (v && v.startsWith("HS")) return c;
        }
    }

    return 0;
}

function findTargetSheet(workbook: ExcelJS.Workbook) {
    let best: any = null;
    
    workbook.eachSheet((sheet) => {
        const { headerRow, headerMap, headerScore } = findHeaderRowAndMap(sheet);
        const effectiveRow = headerRow || 1;
        const hsCol = findHsColumn(sheet, effectiveRow, headerMap);
        
        let score = headerScore;
        if (hsCol) score += 2;

        const candidate = { score, sheet, headerRow: effectiveRow, headerMap, hsCol };
        
        if (!best || score > best.score) {
            best = candidate;
        }
    });

    return best;
}

async function copyYesterdayExcel(baseRoot: string, photographerName: string, targetPath: string) {
    const today = new Date();
    for (let i = 1; i <= 365; i++) { // Python uses 365
        const d = new Date();
        d.setDate(today.getDate() - i);
        
        const yStr = d.getFullYear().toString();
        const mStr = `${(d.getMonth() + 1).toString().padStart(2, '0')}月`;
        const dStr = `${(d.getMonth() + 1).toString().padStart(2, '0')}${d.getDate().toString().padStart(2, '0')}`;
        
        const dir = path.join(baseRoot, `${yStr}相片`, mStr, `${dStr}${photographerName}`);
        const excel = path.join(dir, `${dStr}${photographerName}.xlsx`);
        
        if (await fs.pathExists(excel)) {
            await fs.copy(excel, targetPath);
            return true;
        }
    }
    return false;
}

export async function updateTodayExcel(
  folderNames: string[], 
  baseRoot: string, 
  photographerName: string
): Promise<{ added: number; skipped: number; error?: string }> {
  try {
    const today = new Date();
    const yearStr = today.getFullYear().toString();
    const monthStr = `${(today.getMonth() + 1).toString().padStart(2, '0')}月`;
    const dayStr = `${(today.getMonth() + 1).toString().padStart(2, '0')}${today.getDate().toString().padStart(2, '0')}`;
    
    const todayDir = path.join(baseRoot, `${yearStr}相片`, monthStr, `${dayStr}${photographerName}`);
    await fs.ensureDir(todayDir);
    
    const excelPath = path.join(todayDir, `${dayStr}${photographerName}.xlsx`);
    
    if (!await fs.pathExists(excelPath)) {
      await copyYesterdayExcel(baseRoot, photographerName, excelPath);
    }
    
    if (!await fs.pathExists(excelPath)) {
      return { added: 0, skipped: 0, error: "无法找到或创建今日 Excel 文件" };
    }

    const workbook = new ExcelJS.Workbook();
    await workbook.xlsx.readFile(excelPath);
    
    const picked = findTargetSheet(workbook);
    if (!picked) return { added: 0, skipped: 0, error: "未找到有效的工作表" };

    const { sheet, headerRow, headerMap, hsCol } = picked;
    if (!hsCol) return { added: 0, skipped: 0, error: "无法识别表头 (缺少 HS 列)" };

    if (hsCol === 4) {
        if (!headerMap['name']) headerMap['name'] = 3;
        if (!headerMap['photographer']) headerMap['photographer'] = 2;
    }

    // Find real last data row by scanning HS column
    let lastDataRow = headerRow;
    const maxScanR = sheet.rowCount || headerRow;
    
    const dateCol = headerMap['shoot_date'];
    const dateStr = `${today.getMonth() + 1}月${today.getDate()}日`;

    // Python scans from headerRow + 1
    for (let r = headerRow + 1; r <= maxScanR; r++) {
        const cellHs = sheet.getCell(r, hsCol);
        const vHs = norm(cellHs.text || cellHs.value);
        
        let vSeq = "";
        const seqCol = headerMap['seq'];
        if (seqCol) {
            const cellSeq = sheet.getCell(r, seqCol);
            vSeq = norm(cellSeq.text || cellSeq.value);
        }

        if (vHs || vSeq) {
            lastDataRow = r;
        }
    }
    
    // Calculate next monthly count
    let mcNext = 1;
    const mcCol = headerMap['monthly_count'];
    if (mcCol) {
        let maxMc = 0;
        // Scan backwards
        for (let r = lastDataRow; r > headerRow; r--) {
            const v = sheet.getCell(r, mcCol).value;
            const n = parseInt(String(v || '0'), 10);
            if (!isNaN(n) && n > 0) {
                maxMc = n;
                break;
            }
        }
        mcNext = maxMc + 1;
    }

    // Styles
    const oldFill: ExcelJS.Fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFC6EFCE' } }; // Light Green
    const oldFont: Partial<ExcelJS.Font> = { color: { argb: 'FF006100' } }; // Dark Green

    const newHsFill: ExcelJS.Fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFEB9C' } }; // Yellow
    const newHsFont: Partial<ExcelJS.Font> = { color: { argb: 'FF9C5700' } }; // Dark Brown
    
    // Apply styles to ALL past data
    if (dateCol) {
        const targetDate = norm(dateStr);
        for (let r = lastDataRow; r > headerRow; r--) {
            const val = sheet.getCell(r, dateCol).text || sheet.getCell(r, dateCol).value;
            const v = norm(val);

            if (v && v !== targetDate) {
                 const maxCol = sheet.columnCount || 20;
                 for (let c = 1; c <= maxCol; c++) {
                    if (c >= 11 && c <= 15) continue; // Skip K-O
                    const cell = sheet.getCell(r, c);
                    cell.fill = oldFill;
                    if (cell.font) cell.font = { ...cell.font, ...oldFont };
                    else cell.font = oldFont;
                 }
            }
        }
    }

    let added = 0;
    let skipped = 0;

    for (const line of folderNames) {
        const parsed = parseShootLine(line);
        if (!parsed) {
            skipped++;
            continue;
        }

        const newRow = sheet.getRow(lastDataRow + 1);
        
        // Copy style from previous row
        const baseStyleRow = lastDataRow > headerRow ? lastDataRow : headerRow + 1;
        const baseRow = sheet.getRow(baseStyleRow);
        
        if (baseRow.height) newRow.height = baseRow.height;
        
        const maxCol = sheet.columnCount || 20;
        for (let c = 1; c <= maxCol; c++) {
            const srcCell = baseRow.getCell(c);
            const dstCell = newRow.getCell(c);
            
            // Python parity: copy style objects, never share references
            if (srcCell.style) dstCell.style = deepClone(srcCell.style);
            if (srcCell.font) dstCell.font = deepClone(srcCell.font);
            if (srcCell.border) dstCell.border = deepClone(srcCell.border);
            if (srcCell.alignment) dstCell.alignment = deepClone(srcCell.alignment);
            if (srcCell.protection) dstCell.protection = deepClone(srcCell.protection);
            if (srcCell.numFmt) dstCell.numFmt = srcCell.numFmt;
            
            // Apply New Data Style
            if (c === hsCol) {
                dstCell.fill = newHsFill;
                if (srcCell.font) dstCell.font = { ...srcCell.font, ...newHsFont };
            } else {
                dstCell.fill = { type: 'pattern', pattern: 'none' }; // White/None
                // Keep font but black?
                if (srcCell.font) dstCell.font = { ...srcCell.font, color: { argb: 'FF000000' } };
            }
        }

        // Write Values
        if (headerMap['photographer']) newRow.getCell(headerMap['photographer']).value = photographerName;
        if (headerMap['name']) newRow.getCell(headerMap['name']).value = parsed.name;
        newRow.getCell(hsCol).value = parsed.hs;
        if (headerMap['store']) newRow.getCell(headerMap['store']).value = parsed.store;
        if (headerMap['address']) newRow.getCell(headerMap['address']).value = parsed.address;
        if (headerMap['room']) newRow.getCell(headerMap['room']).value = parsed.room;
        if (headerMap['direction']) newRow.getCell(headerMap['direction']).value = parsed.direction;
        if (headerMap['shoot_date']) newRow.getCell(headerMap['shoot_date']).value = dateStr;
        if (headerMap['seq'] && parsed.seq !== undefined) newRow.getCell(headerMap['seq']).value = parsed.seq;
        if (headerMap['monthly_count']) {
            newRow.getCell(headerMap['monthly_count']).value = mcNext;
            mcNext++;
        }

        newRow.commit();
        lastDataRow++;
        added++;
    }

    await workbook.xlsx.writeFile(excelPath);
    return { added, skipped };

  } catch (error: any) {
    return { added: 0, skipped: 0, error: error.message };
  }
}
