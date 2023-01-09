from functools import wraps
from paramiko.client import SSHClient

from utils.logger import get_logger

class SSHCl(SSHClient):
    """
        A SSH Client used to access server worker and control server execution
    """
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.host = config.get("server")
        self.port = config.get("ssh_port")
        self.user = config.get("ssh_user")
        self.password = config.get("ssh_password")
        self.log = get_logger()
        
        self.load_system_host_keys()
        
    def ping_command(self, command):
        """
            This is a decorator to simply retrieve the output of an ssh command, establishing a connection and ending it by the end of the call
        """
        def decorator(func):
            
            @wraps(func)
            def inner(*args, **kwargs):
                self.log.debug(command)
                self.connect(self.host, port=self.port, username=self.user, password=self.password)
                stdin, stdout, stderr = self.exec_command(command)
                stdin.close()
                
                output, err = [l.strip() for l in stdout.readlines()], [l.strip() for l in stderr.readlines()]
                
                self.log.debug(f"{output}, {err}")
                message = func([output, err], *args, **kwargs)
                
                self.close()
                
                return message
                
            return inner
            
        return decorator

    def attached_command(self, command):
        self.connect(self.host, port=self.port, username=self.user, password=self.password)
        stdin, stdout, stderr = self.exec_command(command, get_pty=True)
        
        return stdin, stdout, stderr
    
    def write_remote_file(self, file, buffer):
        self.connect(self.host, port=self.port, username=self.user, password=self.password)
        ftp = self.open_sftp()
        with ftp.file(file, "w", -1) as f:
            f.write(buffer)
            f.flush()
        ftp.close()
        self.close()
        
    def read_remote_file(self, file):
        self.connect(self.host, port=self.port, username=self.user, password=self.password)
        ftp = self.open_sftp()
        with ftp.file(file, "r", -1) as f:
            lines = f.readlines()
        ftp.close()
        self.close()
        
        return lines
