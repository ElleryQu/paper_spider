import os

def path_join(path, *paths, is_file=False):
    '''
    拼接路径。如果路径目录不存在，则生成其目录。如果对象是文件目录且目录不存在，则生成其父目录。
    '''
    p = os.path.join(path, *paths)

    if is_file:
        os.makedirs(os.path.dirname(p), exist_ok=True)
    else:
        os.makedirs(p, exist_ok=True)

    return p