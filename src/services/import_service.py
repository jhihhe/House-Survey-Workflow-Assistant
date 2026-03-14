import os
import shutil
import time
import errno
from src.utils.fs_utils import resolve_conflict

class ImportTask:
    def __init__(self, callbacks=None):
        """
        callbacks: dict with optional keys:
            - on_start(total_files)
            - on_progress(current_index, total_files, speed_str)
            - on_error(error_msg)
            - on_log(log_msg)
            - on_status_change(status_text)
        """
        self.callbacks = callbacks or {}

    def _call(self, name, *args):
        if name in self.callbacks:
            self.callbacks[name](*args)

    def run(self, task_config):
        src_dir = task_config["src"]
        dst_dir = task_config["dst"]
        kind = task_config.get("kind", "photo")
        label = task_config.get("label", kind)
        
        logs = []
        errors = []
        moved_count = 0
        delete_fail_count = 0
        permission_issue_reported = False

        if not os.path.exists(src_dir):
            logs.append(f"⚠️ {label}: 源目录不存在 (未插入存储卡?)")
            self._call('on_status_change', "未检测到设备")
            return (logs, errors, moved_count, label, delete_fail_count, kind)
            
        try:
            os.makedirs(dst_dir, exist_ok=True)
            
            # Test actual write permission by creating a temporary file
            try:
                test_file = os.path.join(dst_dir, '.perm_test')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception as e:
                logs.append(f"❌ 目标目录无法写入文件 (测试失败): {dst_dir}")
                errors.append(f"写入测试失败: {str(e)}")
                self._call('on_status_change', "无写入权限")
                return (logs, errors, moved_count, label, delete_fail_count, kind)
            
            if not os.access(src_dir, os.R_OK):
                logs.append(f"❌ 源目录不可读: {src_dir}")
                self._call('on_status_change', "无读取权限")
                return (logs, errors, moved_count, label, delete_fail_count, kind)

            files = [f for f in os.listdir(src_dir) if not f.startswith('.')]
            
            if not files:
                logs.append(f"ℹ️ {label}: 源目录为空")
                self._call('on_status_change', "无文件")
                return (logs, errors, moved_count, label, delete_fail_count, kind)
            
            logs.append(f"🚀 开始移动 {label}...")
            total_files = len(files)
            self._call('on_start', total_files)
            
            try:
                same_device = (os.stat(src_dir).st_dev == os.stat(dst_dir).st_dev)
            except Exception:
                same_device = False

            for idx, filename in enumerate(files):
                src_file = os.path.join(src_dir, filename)
                dst_file = resolve_conflict(dst_dir, filename)
                
                speed_str = "0.0 MB/s"
                if os.path.isfile(src_file):
                    try:
                        file_size = os.path.getsize(src_file)
                        if kind == "photo":
                            t0 = time.perf_counter()
                            try:
                                shutil.copy2(src_file, dst_file)
                            except PermissionError:
                                # Fallback to copy if copy2 (metadata) fails
                                shutil.copy(src_file, dst_file)
                            dt = time.perf_counter() - t0
                            moved_count += 1
                            speed_mbps = (file_size / (1024 * 1024)) / dt if dt > 0 else 0.0
                            speed_str = f"{speed_mbps:.1f} MB/s"
                        else:
                            if same_device:
                                shutil.move(src_file, dst_file)
                                moved_count += 1
                                speed_str = "0.0 MB/s"
                            else:
                                t0 = time.perf_counter()
                                try:
                                    shutil.copy2(src_file, dst_file)
                                except PermissionError:
                                    shutil.copy(src_file, dst_file)
                                dt = time.perf_counter() - t0
                                moved_count += 1
                                speed_mbps = (file_size / (1024 * 1024)) / dt if dt > 0 else 0.0
                                speed_str = f"{speed_mbps:.1f} MB/s"
                                try:
                                    os.remove(src_file)
                                except Exception:
                                    delete_fail_count += 1
                                    errors.append(f"{label}: {filename} 已复制，但原卡文件未删除")
                        
                        self._call('on_progress', idx + 1, total_files, speed_str)
                        
                    except Exception as e:
                        if isinstance(e, PermissionError) or getattr(e, "errno", None) in (errno.EPERM, errno.EACCES, 1, 13):
                            if not permission_issue_reported:
                                errors.append(f"权限不足: 无法读写文件。请检查是否有磁盘访问权限。\n源: {src_file}\n目标: {dst_file}")
                                permission_issue_reported = True
                            self._call('on_status_change', "权限不足")
                        else:
                            errors.append(f"{kind} 文件处理失败 {filename}: {str(e)}")
                            
        except Exception as e:
            errors.append(f"{label} 任务异常: {str(e)}")
            
        return (logs, errors, moved_count, label, delete_fail_count, kind)
