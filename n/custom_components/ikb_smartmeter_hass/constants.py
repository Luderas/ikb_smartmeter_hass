"""DLMS-Datentypen und physikalische Einheiten für den Kaifa MA309."""

from enum import IntEnum, unique


@unique
class DataType(IntEnum):
    """DLMS-Datentypen gemäß Blue Book Ed. 12.2.
    
    Referenz: https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf
    """

    NullData            = 0x00
    Array               = 0x01
    Structure           = 0x02
    Boolean             = 0x03
    BitString           = 0x04
    DoubleLong          = 0x05  # int32
    DoubleLongUnsigned  = 0x06  # uint32
    OctetString         = 0x09
    VisibleString       = 0x0A
    Utf8String          = 0x0C
    BinaryCodedDecimal  = 0x0D
    Integer             = 0x0F  # int8
    Long                = 0x10  # int16
    Unsigned            = 0x11  # uint8
    LongUnsigned        = 0x12  # uint16
    CompactArray        = 0x13
    Long64              = 0x14  # int64
    Long64Unsigned      = 0x15  # uint64
    Enum                = 0x16
    Float32             = 0x17
    Float64             = 0x18
    DateTime            = 0x19
    Date                = 0x1A
    Time                = 0x1B


@unique
class PhysicalUnits(IntEnum):
    """DLMS physikalische Einheiten gemäß Blue Book Ed. 12.2.
    
    Referenz: https://www.dlms.com/files/Blue-Book-Ed-122-Excerpt.pdf
    """

    Undef = 0x00  # undefiniert / unbekannt

    W    = 0x1B   # Wirkleistung         [W]
    VA   = 0x1C   # Scheinleistung       [VA]
    var  = 0x1D   # Blindleistung        [var]
    Wh   = 0x1E   # Wirkenergie          [Wh]
    VAh  = 0x1F   # Scheinenergie        [VAh]
    varh = 0x20   # Blindenergie         [varh]
    A    = 0x21   # Strom                [A]
    C    = 0x22   # Ladung               [C]
    V    = 0x23   # Spannung             [V]

    Hz   = 0x2C   # Frequenz             [Hz]

    NoUnit = 0xFF  # dimensionslos
