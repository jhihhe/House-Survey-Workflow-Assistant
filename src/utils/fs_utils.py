import os
import shutil
from datetime import datetime
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
