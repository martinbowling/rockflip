#ifndef HOST_GB_H
#define HOST_GB_H
/* Test shim only. Production compiles against real GBDK headers. */
#include <stdint.h>
typedef uint8_t UBYTE;
typedef uint16_t UWORD;
#define BANKED
extern unsigned host_ram_bank,host_ram_enabled;
#define ENABLE_RAM_MBC5 (host_ram_enabled=1)
#define DISABLE_RAM_MBC5 (host_ram_enabled=0)
#define SWITCH_RAM_MBC5(n) (host_ram_bank=(n))
#endif
