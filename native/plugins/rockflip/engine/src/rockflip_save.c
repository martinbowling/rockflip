#pragma bank 255
#include "rockflip_save.h"

/* SRAM bank 3 only, two independent 4096-byte records at A000 and B000.
 * Header offsets (little endian):
 *   0 'R' commit marker (written LAST); 1 'F'; 2 '0'; 3 '2';
 *   4 version=2; 5 layout=1(generic/old native) or2(snapshot native) or3(weather native) or4(lens native) or5(regionalchallenge native); 6..7 payload bytes; 8..9 sequence;
 *   10..11 CRC16-CCITT-FALSE; 12..15 reserved zero.
 * CRC polynomial 1021, init FFFF, no xor/reflection, covers logical committed
 * header bytes 0..9, then 12..15, then payload. CRC bytes excluded. Thus CRC
 * includes magic, version, layout, length, sequence and reserved metadata.
 * A torn write cannot invalidate the other slot: invalidate destination byte
 * zero, stream its header/payload, store CRC, validate, THEN commit 'R'.
 * No claim about physical cartridge endurance or atomic multi-byte writes.
 */
UBYTE rf_store_ok;
UBYTE rf_store_locked;
UBYTE rf_store_loaded_layout;

/* 512 ROM bytes trade against synchronous save latency. Table generated from
 * polynomial 1021; standard CCITT-FALSE vector remains verified by host tests.
 * This table lives in this function bank, so access needs no ROM bank switch. */
static const UWORD crc_table[256]={
    0x0000u,0x1021u,0x2042u,0x3063u,0x4084u,0x50A5u,0x60C6u,0x70E7u,
    0x8108u,0x9129u,0xA14Au,0xB16Bu,0xC18Cu,0xD1ADu,0xE1CEu,0xF1EFu,
    0x1231u,0x0210u,0x3273u,0x2252u,0x52B5u,0x4294u,0x72F7u,0x62D6u,
    0x9339u,0x8318u,0xB37Bu,0xA35Au,0xD3BDu,0xC39Cu,0xF3FFu,0xE3DEu,
    0x2462u,0x3443u,0x0420u,0x1401u,0x64E6u,0x74C7u,0x44A4u,0x5485u,
    0xA56Au,0xB54Bu,0x8528u,0x9509u,0xE5EEu,0xF5CFu,0xC5ACu,0xD58Du,
    0x3653u,0x2672u,0x1611u,0x0630u,0x76D7u,0x66F6u,0x5695u,0x46B4u,
    0xB75Bu,0xA77Au,0x9719u,0x8738u,0xF7DFu,0xE7FEu,0xD79Du,0xC7BCu,
    0x48C4u,0x58E5u,0x6886u,0x78A7u,0x0840u,0x1861u,0x2802u,0x3823u,
    0xC9CCu,0xD9EDu,0xE98Eu,0xF9AFu,0x8948u,0x9969u,0xA90Au,0xB92Bu,
    0x5AF5u,0x4AD4u,0x7AB7u,0x6A96u,0x1A71u,0x0A50u,0x3A33u,0x2A12u,
    0xDBFDu,0xCBDCu,0xFBBFu,0xEB9Eu,0x9B79u,0x8B58u,0xBB3Bu,0xAB1Au,
    0x6CA6u,0x7C87u,0x4CE4u,0x5CC5u,0x2C22u,0x3C03u,0x0C60u,0x1C41u,
    0xEDAEu,0xFD8Fu,0xCDECu,0xDDCDu,0xAD2Au,0xBD0Bu,0x8D68u,0x9D49u,
    0x7E97u,0x6EB6u,0x5ED5u,0x4EF4u,0x3E13u,0x2E32u,0x1E51u,0x0E70u,
    0xFF9Fu,0xEFBEu,0xDFDDu,0xCFFCu,0xBF1Bu,0xAF3Au,0x9F59u,0x8F78u,
    0x9188u,0x81A9u,0xB1CAu,0xA1EBu,0xD10Cu,0xC12Du,0xF14Eu,0xE16Fu,
    0x1080u,0x00A1u,0x30C2u,0x20E3u,0x5004u,0x4025u,0x7046u,0x6067u,
    0x83B9u,0x9398u,0xA3FBu,0xB3DAu,0xC33Du,0xD31Cu,0xE37Fu,0xF35Eu,
    0x02B1u,0x1290u,0x22F3u,0x32D2u,0x4235u,0x5214u,0x6277u,0x7256u,
    0xB5EAu,0xA5CBu,0x95A8u,0x8589u,0xF56Eu,0xE54Fu,0xD52Cu,0xC50Du,
    0x34E2u,0x24C3u,0x14A0u,0x0481u,0x7466u,0x6447u,0x5424u,0x4405u,
    0xA7DBu,0xB7FAu,0x8799u,0x97B8u,0xE75Fu,0xF77Eu,0xC71Du,0xD73Cu,
    0x26D3u,0x36F2u,0x0691u,0x16B0u,0x6657u,0x7676u,0x4615u,0x5634u,
    0xD94Cu,0xC96Du,0xF90Eu,0xE92Fu,0x99C8u,0x89E9u,0xB98Au,0xA9ABu,
    0x5844u,0x4865u,0x7806u,0x6827u,0x18C0u,0x08E1u,0x3882u,0x28A3u,
    0xCB7Du,0xDB5Cu,0xEB3Fu,0xFB1Eu,0x8BF9u,0x9BD8u,0xABBBu,0xBB9Au,
    0x4A75u,0x5A54u,0x6A37u,0x7A16u,0x0AF1u,0x1AD0u,0x2AB3u,0x3A92u,
    0xFD2Eu,0xED0Fu,0xDD6Cu,0xCD4Du,0xBDAAu,0xAD8Bu,0x9DE8u,0x8DC9u,
    0x7C26u,0x6C07u,0x5C64u,0x4C45u,0x3CA2u,0x2C83u,0x1CE0u,0x0CC1u,
    0xEF1Fu,0xFF3Eu,0xCF5Du,0xDF7Cu,0xAF9Bu,0xBFBAu,0x8FD9u,0x9FF8u,
    0x6E17u,0x7E36u,0x4E55u,0x5E74u,0x2E93u,0x3EB2u,0x0ED1u,0x1EF0u,
};
static UWORD crc_byte(UWORD crc, UBYTE value) {
    return (crc << 8) ^ crc_table[(UBYTE)(crc >> 8) ^ value];
}

static volatile UBYTE *slot_pointer(UBYTE slot) {
    return (volatile UBYTE *)(slot ? 0xB000u : 0xA000u);
}

static UWORD read_word(volatile UBYTE *p, UBYTE offset) {
    return (UWORD)p[offset] | ((UWORD)p[offset+1] << 8);
}

static UWORD record_crc(volatile UBYTE *p, UWORD size) {
    UWORD crc=0xFFFFu, i;
    crc=crc_byte(crc,'R');
    for (i=1; i<10; ++i) crc=crc_byte(crc,p[i]);
    for (i=12; i<16; ++i) crc=crc_byte(crc,p[i]);
    for (i=0; i<size; ++i) crc=crc_byte(crc,p[16+i]);
    return crc;
}

/* Refuse to overwrite a committed future marker, even if this older program
 * cannot authenticate the future checksum/layout. Partial writes with byte0=0
 * are not future records. Unsupported RF02 version/layout also locks writes. */
static UBYTE layout_for_size(UWORD size) {
    if (size==RF_STORE_WEATHER_SIZE) return 6;
    if (size==RF_STORE_SNAPSHOT_SIZE) return 2;
    return 1;
}
static UBYTE layout_size_valid(UBYTE layout,UWORD size) {
    if (layout==3 || layout==4 || layout==5 || layout==6) return size==RF_STORE_WEATHER_SIZE;
    if (layout==2) return size==RF_STORE_SNAPSHOT_SIZE;
    if (layout!=1) return 0;
    return size!=RF_STORE_SNAPSHOT_SIZE && size!=RF_STORE_WEATHER_SIZE;
}
static UBYTE can_migrate(UBYTE layout,UWORD stored,UWORD requested) {
    if ((layout==3 || layout==4 || layout==5) && stored==RF_STORE_WEATHER_SIZE && requested==RF_STORE_WEATHER_SIZE) return 1;
    if (layout==1 && stored==RF_STORE_PRE_SNAPSHOT_SIZE) {
        if (requested==RF_STORE_SNAPSHOT_SIZE || requested==RF_STORE_WEATHER_SIZE) return 1;
    }
    if (layout==2 && stored==RF_STORE_SNAPSHOT_SIZE && requested==RF_STORE_WEATHER_SIZE) return 1;
    return 0;
}
static UBYTE unsupported(volatile UBYTE *p) {
    if (p[0]!='R' || p[1]!='F') return 0;
    if (p[2]>='0' && p[2]<='9' && p[3]>='0' && p[3]<='9') {
        if (p[2]>'0' || (p[2]=='0' && p[3]>'2')) return 1;
    }
    if (p[2]!='0' || p[3]!='2') return 0;
    if (p[4]!=2 || !layout_size_valid(p[5],read_word(p,6))) return 1;
    return 0;
}
static UBYTE valid_record(volatile UBYTE *p, UBYTE committed) {
    UWORD size;
    UBYTE i;
    if ((committed && p[0]!='R') || p[1]!='F' || p[2]!='0' || p[3]!='2' || p[4]!=2) return 0;
    size=read_word(p,6);
    if (!size || size>RF_STORE_PAYLOAD_MAX || !layout_size_valid(p[5],size)) return 0;
    for (i=12; i<16; ++i) if (p[i]) return 0;
    return record_crc(p,size)==read_word(p,10);
}

static UBYTE valid_legacy(volatile UBYTE *p) {
    UBYTE sum=0, i;
    if (p[0]!='R' || p[1]!='F' || p[2]!='0' || p[3]!='1') return 0;
    for (i=0; i<63; ++i) sum+=p[i];
    return sum==p[63];
}

/* Signed modular ordering without relying on implementation-defined cast.
 * Writes differ by one; half-cycle ambiguity/equal sequences choose slot one. */
static UBYTE newest(UBYTE good0, UBYTE good1) {
    UWORD difference;
    if (!good0) return 1;
    if (!good1) return 0;
    difference=read_word(slot_pointer(1),8)-read_word(slot_pointer(0),8);
    return !difference || difference<=0x8000u;
}

static void close_ram(void) {
    SWITCH_RAM_MBC5(0);
    DISABLE_RAM_MBC5;
}

UBYTE rf_store_load(void *payload, UWORD size, UBYTE *legacy64) BANKED {
    volatile UBYTE *p;
    UBYTE a,b,result=0;
    UWORD i,stored_size;
    rf_store_ok=0;rf_store_locked=0;
    rf_store_loaded_layout=0;
    if (!payload || !size || size>RF_STORE_PAYLOAD_MAX) return 0;
    ENABLE_RAM_MBC5;SWITCH_RAM_MBC5(3);
    if (unsupported(slot_pointer(0)) || unsupported(slot_pointer(1))) {
        rf_store_locked=1;result=3;
    } else {
        a=valid_record(slot_pointer(0),1);b=valid_record(slot_pointer(1),1);
        if (a || b) {
            p=slot_pointer(newest(a,b));
            stored_size=read_word(p,6);
            rf_store_loaded_layout=p[5];
            if (can_migrate(p[5],stored_size,size)) {
                /* Append-only migration: keep every old payload byte and
                 * zero appended poses/conditions as needed. No second WRAM payload. */
                for (i=0; i<stored_size; ++i) ((UBYTE *)payload)[i]=p[16+i];
                for (; i<size; ++i) ((UBYTE *)payload)[i]=0;
                rf_store_ok=1;result=4;
            } else if (stored_size!=size
                || p[5]!=layout_for_size(size)) {rf_store_locked=1;result=3;}
            else {
                for (i=0; i<size; ++i) ((UBYTE *)payload)[i]=p[16+i];
                rf_store_ok=1;result=1;
            }
        } else if (legacy64 && valid_legacy(slot_pointer(0))) {
            p=slot_pointer(0);
            for (i=0; i<64; ++i) legacy64[i]=p[i];
            rf_store_ok=1;result=2;
        }
    }
    close_ram();return result;
}

void rf_store_save(const void *payload, UWORD size) BANKED {
    volatile UBYTE *p;
    UBYTE a,b,destination,i,layout;
    UWORD sequence=0,crc,j,stored_size;
    rf_store_ok=0;
    if (rf_store_locked || !payload || !size || size>RF_STORE_PAYLOAD_MAX) return;
    ENABLE_RAM_MBC5;SWITCH_RAM_MBC5(3);
    if (unsupported(slot_pointer(0)) || unsupported(slot_pointer(1))) {
        rf_store_locked=1;close_ram();return;
    }
    a=valid_record(slot_pointer(0),1);b=valid_record(slot_pointer(1),1);
    if (a || b) {
        destination=newest(a,b);
        p=slot_pointer(destination);
        stored_size=read_word(p,6);
        if (!can_migrate(p[5],stored_size,size)
            && (stored_size!=size || p[5]!=layout_for_size(size))) {
            rf_store_locked=1;close_ram();return;
        }
        sequence=read_word(p,8)+1u;
        destination^=1;
    } else {
        /* First migration write preserves all 64 RF01 bytes in slot zero. */
        destination=valid_legacy(slot_pointer(0)) ? 1 : 0;
    }
    p=slot_pointer(destination);layout=layout_for_size(size);
    p[0]=0;p[1]='F';p[2]='0';p[3]='2';p[4]=2;p[5]=layout;
    p[6]=(UBYTE)size;p[7]=(UBYTE)(size>>8);
    p[8]=(UBYTE)sequence;p[9]=(UBYTE)(sequence>>8);
    p[10]=p[11]=0;
    for (i=12; i<16; ++i) p[i]=0;
    /* Compute from the stable source while writing; readback CRC below detects
     * a failed byte write rather than blessing corruption already in SRAM. */
    crc=0xFFFFu;crc=crc_byte(crc,'R');
    crc=crc_byte(crc,'F');crc=crc_byte(crc,'0');crc=crc_byte(crc,'2');
    crc=crc_byte(crc,2);crc=crc_byte(crc,layout);
    crc=crc_byte(crc,(UBYTE)size);crc=crc_byte(crc,(UBYTE)(size>>8));
    crc=crc_byte(crc,(UBYTE)sequence);crc=crc_byte(crc,(UBYTE)(sequence>>8));
    for (i=12; i<16; ++i) crc=crc_byte(crc,0);
    for (j=0; j<size; ++j) {
        UBYTE value=((const UBYTE *)payload)[j];
        p[16+j]=value;crc=crc_byte(crc,value);
    }
    p[10]=(UBYTE)crc;p[11]=(UBYTE)(crc>>8);
    if (valid_record(p,0)) {
        /* Precommit readback already validated every metadata/payload byte.
         * Only the final commit byte changed; verify that byte directly instead
         * of rescanning the full payload a second time. */
        p[0]='R';rf_store_ok=p[0]=='R';
    }
    close_ram();
}
