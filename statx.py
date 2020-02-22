# https://raw.githubusercontent.com/ckarageorgkaneen/pystatx/master/statx.py
"""statx(2) linux system call wrapper.

statx - get file status (extended)

http://man7.org/linux/man-pages/man2/statx.2.html
"""
import platform
import ctypes
import functools

__MACHINE = platform.machine()
__x86_64__ = __MACHINE == 'x86_64'
__arm64__ = __MACHINE.startswith('arm') or __MACHINE.startswith('aarch')
__x86__ = __MACHINE == 'i386' or __MACHINE == 'i686'

if __x86_64__:
    __NR_statx = 332
elif __arm64__:
    __NR_statx = 291
elif __x86__:
    __NR_statx = 383
else:
    raise EnvironmentError(
        'Only x86, arm64 and x86_64 machines are supported.')

# from kernel-sources include/linux/fcntl.h
AT_SYMLINK_NOFOLLOW = 0x100  # Do not follow symbolic links.
AT_NO_AUTOMOUNT = 0x800  # Suppress terminal automount traversal
AT_FDCWD = -100  # Special value used to indicate
# openat should use the current working directory.
AT_STATX_SYNC_TYPE = 0x6000  # Type of synchronisation required from statx()
AT_STATX_FORCE_SYNC = 0x2000  # Force the attributes to be sync'd
# with the server
AT_STATX_DONT_SYNC = 0x4000  # Don't sync attributes with the server

# from kernel-sources include/uapi/linux/stat.h
S_IFMT = 0o170000
S_IFSOCK = 0o140000
S_IFLNK = 0o120000
S_IFREG = 0o100000
S_IFBLK = 0o60000
S_IFDIR = 0o40000
S_IFCHR = 0o20000
S_IFIFO = 0o10000
STATX_TYPE = 0x00000001  # Want/got stx_mode & S_IFMT
STATX_MODE = 0x00000002  # Want/got stx_mode & ~S_IFMT
STATX_NLINK = 0x00000004  # Want/got stx_nlink
STATX_UID = 0x00000008  # Want/got stx_uid
STATX_GID = 0x00000010  # Want/got stx_gid
STATX_ATIME = 0x00000020  # Want/got stx_atime
STATX_MTIME = 0x00000040  # Want/got stx_mtime
STATX_CTIME = 0x00000080  # Want/got stx_ctime
STATX_INO = 0x00000100  # Want/got stx_ino
STATX_SIZE = 0x00000200  # Want/got stx_size
STATX_BLOCKS = 0x00000400  # Want/got stx_blocks
STATX_BASIC_STATS = 0x000007ff  # The stuff in the normal stat struct
STATX_BTIME = 0x00000800  # Want/got stx_btime
STATX_ALL = 0x00000fff  # All currently supported flags


class _struct_statx_timestamp(ctypes.Structure):
    """File timestamps struct."""

    _fields_ = [
        ('tv_sec', ctypes.c_longlong),  # Seconds since the Epoch (UNIX time)
        ('tv_nsec', ctypes.c_uint),  # Nanoseconds since tv_sec
        ('__statx_timestamp_pad1', ctypes.c_int * 1)
    ]


class _struct_statx(ctypes.Structure):
    """Returned buffer struct."""
    _fields_ = [
        ('stx_mask', ctypes.c_uint),  # Mask of bits indicating filled fields
        ('stx_blksize', ctypes.c_uint),  # Block size for filesystem I/O
        ('stx_attributes',
         ctypes.c_ulonglong),  # Extra file attribute indicators
        ('stx_nlink', ctypes.c_uint),  # Number of hard links
        ('stx_uid', ctypes.c_uint),  # User ID of owner
        ('stx_gid', ctypes.c_uint),  # Group ID of owner
        ('stx_mode', ctypes.c_ushort),  # File type and mode
        ('__statx_pad1', ctypes.c_ushort * 1),
        ('stx_ino', ctypes.c_ulonglong),  # Inode number
        ('stx_size', ctypes.c_ulonglong),  # Total size in bytes
        ('stx_blocks', ctypes.c_ulonglong),  # Number of 512B blocks allocated
        ('stx_attributes_mask',
         ctypes.c_ulonglong),  # Mask to show what's supported
        # in stx_attributes

        # The following fields are file timestamps
        ('stx_atime', _struct_statx_timestamp),  # Last access
        ('stx_btime', _struct_statx_timestamp),  # Creation
        ('stx_ctime', _struct_statx_timestamp),  # Last status change
        ('stx_mtime', _struct_statx_timestamp),  # Last modification

        # If this file represents a device, then the next two
        # fields contain the ID of the device
        ('stx_rdev_major', ctypes.c_uint),  # Major ID
        ('stx_rdev_minor', ctypes.c_uint),  # Minor ID

        # The next two fields contain the ID of the device
        # containing the filesystem where the file resides
        ('stx_dev_major', ctypes.c_uint),  # Major ID
        ('stx_dev_minor', ctypes.c_uint),  # Minor ID
        ('__statx_pad2', ctypes.c_ulonglong * 14)
    ]


def _stx_timestamp(struct_statx_timestamp):
    """Return statx timestamp."""
    return struct_statx_timestamp.tv_sec + \
        struct_statx_timestamp.tv_nsec * 1e-9


_syscall = ctypes.CDLL(None).syscall
_syscall.restype = ctypes.c_int
_syscall.argtypes = [
    ctypes.c_long, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_uint,
    ctypes.POINTER(_struct_statx)
]
_statx = functools.partial(_syscall, __NR_statx)


class statx(object):
    """statx system call wrapper class."""
    def __init__(self,
                 filepath,
                 no_automount=False,
                 follow_symlinks=True,
                 get_basic_stats=False,
                 get_filesize_only=False,
                 force_sync=False,
                 dont_sync=False):
        """statx wrapper class constructor."""
        self._dirfd = AT_FDCWD
        self._flag = AT_SYMLINK_NOFOLLOW
        self._mask = STATX_ALL
        if no_automount:
            self._flag |= AT_NO_AUTOMOUNT
        if follow_symlinks:
            self._flag &= ~AT_SYMLINK_NOFOLLOW
        if get_basic_stats:
            self._mask &= ~STATX_BASIC_STATS
        if get_filesize_only:
            self._mask = STATX_SIZE
        if force_sync:
            self._flag &= ~AT_STATX_SYNC_TYPE
            self._flag |= AT_STATX_FORCE_SYNC
        if dont_sync:
            self._flag &= ~AT_STATX_SYNC_TYPE
            self._flag |= AT_STATX_DONT_SYNC
        self._struct_statx_buf = _struct_statx()
        _statx(self._dirfd, filepath.encode(), self._flag, self._mask,
               self._struct_statx_buf)

    @property
    def mask(self):
        """Return mask of bits indicating filled fields."""
        return self._struct_statx_buf.stx_mask

    @property
    def blksize(self):
        """Return block size for filesystem I/O."""
        return self._struct_statx_buf.stx_blksize

    @property
    def nlink(self):
        """Return number of hard links."""
        if self.mask & STATX_NLINK:
            return self._struct_statx_buf.stx_nlink
        return None

    @property
    def dev(self):
        """Return device ID."""
        return hex(self._struct_statx_buf.stx_dev_major), hex(
            self._struct_statx_buf.stx_dev_minor)

    @property
    def rdev(self):
        """Return file device ID."""
        if self.mask & STATX_TYPE:
            if (self._struct_statx_buf.stx_mode & S_IFMT == S_IFBLK or
                    self._struct_statx_buf.stx_mode & S_IFMT == S_IFCHR):
                return hex(self._struct_statx_buf.stx_rdev_major), hex(
                    self._struct_statx_buf.stx_rdev_minor)
        return None

    @property
    def uid(self):
        """Return user ID of owner."""
        if self.mask & STATX_UID:
            return self._struct_statx_buf.stx_uid
        return None

    @property
    def gid(self):
        """Return group ID of owner."""
        if self.mask & STATX_GID:
            return self._struct_statx_buf.stx_gid
        return None

    @property
    def filetype(self):
        """Return file type."""
        if self.mask & STATX_TYPE:
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFIFO:
                return 'FIFO'
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFCHR:
                return 'character special file'
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFDIR:
                return 'directory'
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFBLK:
                return 'block special file'
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFREG:
                return 'regular file'
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFLNK:
                return 'symbolic link'
            if self._struct_statx_buf.stx_mode & S_IFMT == S_IFSOCK:
                return 'socket'
            return 'unknown type {}'.format(
                oct(self._struct_statx_buf.stx_mode & S_IFMT))
        return 'no type'

    @property
    def mode(self):
        """Return file mode."""
        if self.mask & STATX_MODE:
            return oct(self._struct_statx_buf.stx_mode & 0o7777)
        return None

    @property
    def ino(self):
        """Return inode number."""
        if self.mask & STATX_INO:
            return self._struct_statx_buf.stx_ino
        return None

    @property
    def size(self):
        """Return total size in bytes."""
        if self.mask & STATX_SIZE:
            return self._struct_statx_buf.stx_size
        return None

    @property
    def blocks(self):
        """Return number of 512B blocks allocated."""
        if self.mask & STATX_BLOCKS:
            return self._struct_statx_buf.stx_blocks
        return None

    @property
    def atime(self):
        """Return the last access time."""
        if self.mask & STATX_ATIME:
            return _stx_timestamp(self._struct_statx_buf.stx_atime)
        return None

    @property
    def btime(self):
        """Return the birth time."""
        if self.mask & STATX_BTIME:
            return _stx_timestamp(self._struct_statx_buf.stx_btime)
        return None

    @property
    def ctime(self):
        """Return the change time."""
        if self.mask & STATX_CTIME:
            return _stx_timestamp(self._struct_statx_buf.stx_ctime)
        return None

    @property
    def mtime(self):
        """Return the modification time."""
        if self.mask & STATX_MTIME:
            return _stx_timestamp(self._struct_statx_buf.stx_mtime)
        return None