/*
 * Test the PTR implementation.
 */

#include "vimlac.h"
#include "ptr.h"

#define TIMEOUT 5000


int
main(int argc, char *argv[])
{
    ptr_mount("test1.ptp");
    ptr_start();
    while (true)
    {
        int timeout;
        unsigned char ch;

        timeout = TIMEOUT;
        while (!ptr_ready())
        {
            ptr_tick(2);
            if (--timeout < 0)
            {
                printf("TIMEOUT\n");
                return 0;
            }
        }

        ch = ptr_read();
        printf("byte is %4.4o (0x%02x)\n", ch, ch);

        timeout = TIMEOUT;
        while (ptr_ready())
        {
            ptr_tick(2);
            if (--timeout < 0)
            {
                printf("TIMEOUT\n");
                return 0;
            }
        }
    }
}
