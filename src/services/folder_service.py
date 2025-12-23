import os
from ..utils.fs_utils import get_date_based_dirs

class FolderService:
    @staticmethod
    def create_folders(folder_names, callback=None):
        """
        callback: func(action, value)
            action: 'init' (value=total_steps), 'step' (value=current_step)
        """
        target_dirs = get_date_based_dirs()
        # Create base dirs
        for d in target_dirs:
            try:
                os.makedirs(d, exist_ok=True)
            except OSError as e:
                return None, [f"无法创建目录 {d}: {e}"], target_dirs

        total_steps = len(folder_names) * len(target_dirs)
        if callback:
            callback('init', total_steps)
            
        success_by_dir = {d: 0 for d in target_dirs}
        errors = []
        
        step_count = 0
        for name in folder_names:
            valid_name = name.replace('/', '／').replace('\\', '＼')
            for base in target_dirs:
                try:
                    full_path = os.path.join(base, valid_name)
                    os.makedirs(full_path, exist_ok=False)
                    success_by_dir[base] += 1
                except FileExistsError:
                    errors.append(f"{base} 中 '{name}' 已存在")
                except Exception as e:
                    errors.append(f"{base} 中 '{name}' 创建失败: {e}")
                finally:
                    step_count += 1
                    if callback:
                        callback('step', step_count)
                        
        return success_by_dir, errors, target_dirs
