
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

def decode_geometry(geom : QByteArray):

    """ Decode Qt's internal geometry format into readable values.
        """
    
    ds = QDataStream(geom, QIODevice.ReadOnly)
    ds.setVersion(QDataStream.Qt_5_6)  # matches Qt's encoding version

    # Format:
    #   0: magic number (ignored)
    #   1: major version
    #   2: minor version
    #   3: x
    #   4: y
    #   5: width
    #   6: height
    #   7: maximized (bool)
    #   8: fullscreen (bool)

    try:
        magic = ds.readUInt32()
        major = ds.readUInt16()
        minor = ds.readUInt16()

        x = ds.readInt32()
        y = ds.readInt32()
        w = ds.readInt32()
        h = ds.readInt32()

        maximized = ds.readBool()
        fullscreen = ds.readBool()

        print("Decoded geometry:")
        print(f"  magic      = {magic}")
        print(f"  version    = {major}.{minor}")
        print(f"  x          = {x}")
        print(f"  y          = {y}")
        print(f"  width      = {w}")
        print(f"  height     = {h}")
        print(f"  maximized  = {maximized}")
        print(f"  fullscreen = {fullscreen}")

    except Exception as e:
        print(f"Failed decoding geometry: {e}")
