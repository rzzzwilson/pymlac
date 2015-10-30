/*
 * Simple program to write a test PTR file.
 */

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int
main(void)
{
    int fd = open("test.ptr", O_WRONLY|O_CREAT);

    write(fd, "\0\1\2", 3);

    close(fd);

    return 0;
}
