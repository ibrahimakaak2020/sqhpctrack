import os
import platform
from flask import current_app

def mount_network_share():
    """Helper function to mount network shares if needed"""
    if platform.system() == 'Windows':
        # Windows network share mounting
        if not os.path.exists( r'\\DESKTOP-00F5K47\\storge'):

            share_path =  r'\\DESKTOP-00F5K47\\storge'.replace('\\', '/')
            net_use = f"net use {share_path}"
            print(f"Mounted network share: {share_path}")
            os.system(net_use)
            
    elif platform.system() == 'Linux':
        # Linux mount command
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            mount_point = current_app.config['UPLOAD_FOLDER']
            os.makedirs(mount_point, exist_ok=True)
            mount_cmd = f"mount -t cifs //server/share {mount_point} -o username=user,password=pass"
            os.system(mount_cmd)

def check_network_path():
    """Verify network path is accessible"""
    test_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'test.tmp')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        return True
    except Exception as e:
        current_app.logger.error(f"Network path check failed: {e}")
        return False