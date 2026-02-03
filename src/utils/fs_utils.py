import os
import shutil
from datetime import datetime, timedelta
from .config import Config

def resolve_conflict(dst_dir, filename):
    dst_file = os.path.join(dst_dir, filename)
    if not os.path.exists(dst_file):
        return dst_file
    base, ext = os.path.splitext(filename)
    counter = 1
    while counter < 1000:
        new_name = f"{base}_{counter}{ext}"
        new_dst = os.path.join(dst_dir, new_name)
        if not os.path.exists(new_dst):
            return new_dst
        counter += 1
    return dst_file

def get_date_based_dirs(base_root=None, mode='create'):
    """
    mode: 'create' (default) -> for generating folders
          'import' -> for importing files (原片)
    """
    if base_root is None:
        base_root = Config.PATHS['root']
    
    today = datetime.now()
    year_str = today.strftime("%Y")
    month_str = f"{today.month:02d}月"
    day_str = f"{today.month:02d}{today.day:02d}"
    
    if mode == 'import':
        # 导入模式: 统一使用 '原片' 后缀
        # 格式: .../{YYYY}相片/{MM}月/{MMDD}原片
        photo_dir = os.path.join(base_root, f"{year_str}相片", month_str, f"{day_str}原片")
        # 格式: .../{YYYY}VR/{MM}月/{MMDD}原片
        vr_dir = os.path.join(base_root, f"{year_str}VR", month_str, f"{day_str}原片")
    else:
        # 创建模式: 相片使用 '贺志', VR 无后缀
        # 格式: .../{YYYY}相片/{MM}月/{MMDD}贺志
        photo_dir = os.path.join(base_root, f"{year_str}相片", month_str, f"{day_str}贺志")
        # 格式: .../{YYYY}VR/{MM}月/{MMDD}
        vr_dir = os.path.join(base_root, f"{year_str}VR", month_str, day_str)
    
    return [photo_dir, vr_dir]

def copy_yesterday_excel_to_today(base_root=None):
    if base_root is None:
        base_root = Config.PATHS['root']
    try:
        today = datetime.now()
        today_dirs = get_date_based_dirs(base_root=base_root, mode='create')
        today_photo_dir = today_dirs[0]
        today_day_str = f"{today.month:02d}{today.day:02d}"
        os.makedirs(today_photo_dir, exist_ok=True)

        source_excel = None
        for delta in range(1, 366):
            candidate = today - timedelta(days=delta)
            y_year_str = candidate.strftime("%Y")
            y_month_str = f"{candidate.month:02d}月"
            y_day_str = f"{candidate.month:02d}{candidate.day:02d}"
            candidate_dir = os.path.join(
                base_root,
                f"{y_year_str}相片",
                y_month_str,
                f"{y_day_str}贺志",
            )
            candidate_excel = os.path.join(
                candidate_dir,
                f"{y_day_str}贺志.xlsx",
            )
            if os.path.exists(candidate_excel):
                source_excel = candidate_excel
                break

        if not source_excel:
            return False

        today_excel = os.path.join(
            today_photo_dir,
            f"{today_day_str}贺志.xlsx",
        )
        shutil.copy2(source_excel, today_excel)
        return True
    except Exception:
        return False

def is_same_device(src, dst):
    try:
        if not os.path.exists(src) or not os.path.exists(dst):
            # If destination doesn't exist, check parent
            dst_check = dst if os.path.exists(dst) else os.path.dirname(dst)
            # If src doesn't exist, can't check, assume False
            if not os.path.exists(src):
                return False
            return os.stat(src).st_dev == os.stat(dst_check).st_dev
        return os.stat(src).st_dev == os.stat(dst).st_dev
    except Exception:
        return False
