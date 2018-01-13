# Inherit activation sockets from systemd, see systemd man page for
# sd_listen_fds().
import socket
from systemd import daemon, journal

SD_LISTEN_FDS_START = 3


def _set_close_on_exec(fds):
    try:
        import fcntl
    except ImportError:
        return
    if not hasattr(fcntl, 'FD_CLOEXEC'):
        return
    for fd in range(SD_LISTEN_FDS_START, SD_LISTEN_FDS_START + fds):
        fcntl.fcntl(fd, fcntl.F_SETFD, fcntl.FD_CLOEXEC)


def map_fds():
    """Return the list of inherited sockets.
    Return null if there arenone.
    """
    fds = {}
    for frozen_fd in frozenset(daemon.listen_fds()):
        journal.send("processing fd: {0}".format(frozen_fd))
        if daemon.is_socket(frozen_fd):
            sock_obj = socket.socket(fileno=frozen_fd)
            journal.send("created socket: name={0}"
                         .format(sock_obj.getsockname()))
            fds[frozen_fd] = sock_obj
    return fds


def get_systemd_socket():
    """Return the inherited socket, if there is one.  If not, return None."""
    map = map_fds()
    if not map:
        return None
    # if num > 1:
    #    raise OSError('only one inherited socket supported')
    sock = map[SD_LISTEN_FDS_START]
    return sock
