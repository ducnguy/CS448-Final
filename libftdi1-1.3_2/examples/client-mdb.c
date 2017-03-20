/* simple.c

   Simple libftdi usage example

   This program is distributed under the GPL, version 2
*/

#include <stdio.h>
#include <stdlib.h>
#include <ftdi.h>
#include <unistd.h>
#include <string.h>

#define OK       0
#define NO_INPUT 1
#define TOO_LONG 2
#define MAX_BITS_TRACKED 128
#define MAX_NAME_LENGTH 12

char *int2bin(int a, char *buffer, int buf_size) {
    buffer += (buf_size - 1);

    for (int i = 31; i >= 0; i--) {
        *buffer-- = (a & 1) + '0';

        a >>= 1;
    }

    return buffer;
}

char *bin(uint32_t x, char* buffer)
{
    int bits = 8;
    for (size_t i = 0; i < bits ; i++) {
       buffer[bits - i - 1] = (x & 1) ? '1' : '0';
       x >>= 1;
    }
    buffer[bits] = '\0';
    return buffer;
}

void printbinchar(char character)
{
    char output[9];
    output[8] = '\0';
    int2bin(character, output, 8);
    printf("%s\n", output);
}

int getLine (char *prmpt, char *buff, size_t sz) {
    int ch, extra;

    // Get line with buffer overrun protection.
    if (prmpt != NULL) {
        printf ("%s", prmpt);
        fflush (stdout);
    }
    if (fgets (buff, sz, stdin) == NULL)
        return NO_INPUT;

    // If it was too long, there'll be no newline. In that case, we flush
    // to end of line so that excess doesn't affect the next call.
    if (buff[strlen(buff)-1] != '\n') {
        extra = 0;
        while (((ch = getchar()) != '\n') && (ch != EOF))
            extra = 1;
        return (extra == 1) ? TOO_LONG : OK;
    }

    // Otherwise remove newline and give string back to caller.
    buff[strlen(buff)-1] = '\0';
    return OK;
}

int mdb_init(struct ftdi_context** ftdi_ptr)
{
    int ret;
    struct ftdi_context* ftdi;
    struct ftdi_version_info version;
    if ((ftdi = ftdi_new()) == 0)
    {
        fprintf(stderr, "ftdi_new failed\n");
        return -1;
    }

    version = ftdi_get_library_version();
    printf("Initialized libftdi %s (major: %d, minor: %d, micro: %d, snapshot ver: %s)\n\n",
        version.version_str, version.major, version.minor, version.micro,
        version.snapshot_str);

    if ((ret = ftdi_set_interface(ftdi, INTERFACE_B)) < 0)
        fprintf(stderr, "unable to set INTERFACE_B: %d (%s)\n", ret, ftdi_get_error_string(ftdi));

    if ((ret = ftdi_usb_open(ftdi, 0x0403, 0x6010)) < 0)
    {
        fprintf(stderr, "unable to open ftdi device: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        return -1;
    }

    if ((ret = ftdi_set_baudrate(ftdi, 115200)) < 0)
        fprintf(stderr, "unable to set baudrate: %d (%s)\n", ret, ftdi_get_error_string(ftdi));

    if ((ret = ftdi_set_line_property(ftdi, BITS_8, STOP_BIT_1, NONE)) < 0)
        fprintf(stderr, "unable to set line property: %d (%s)\n", ret, ftdi_get_error_string(ftdi));

    if ((ret = ftdi_setflowctrl(ftdi, SIO_RTS_CTS_HS)) < 0)
        fprintf(stderr, "unable to set flow control: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
    *ftdi_ptr = ftdi;

    // CLEAR UART
    if ((ret = ftdi_setdtr_rts(ftdi, 1, 0)) < 0)
        fprintf(stderr, "unable to reset UART: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
    if ((ret = ftdi_setdtr_rts(ftdi, 1, 1)) < 0)
        fprintf(stderr, "unable to reset UART: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
    unsigned char buf[200];
    ftdi_read_data(ftdi, buf, sizeof(buf));

    return 0;
}

void mdb_advance_state(struct ftdi_context* ftdi)
{
    int ret;
    if ((ret = ftdi_setdtr(ftdi, 0)) < 0)
        fprintf(stderr, "unable to set dtr to 0: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
    if ((ret = ftdi_setdtr(ftdi, 1)) < 0)
        fprintf(stderr, "unable to set dtr to 1: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
}

int mdb_read_state(struct ftdi_context* ftdi, unsigned char* buf, int size)
{
    int ret;
    if ((ret = ftdi_setrts(ftdi, 0)) < 0)
        fprintf(stderr, "unable to set rts to 0: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
    int bytesRead = ftdi_read_data(ftdi, buf, size);
    if ((ret = ftdi_setrts(ftdi, 1)) < 0)
        fprintf(stderr, "unable to set rts to 1: %d (%s)\n", ret, ftdi_get_error_string(ftdi));

    return bytesRead;
}

void mdb_step(struct ftdi_context* ftdi, char** names, int numNames)
{
    mdb_advance_state(ftdi);

    unsigned char buf[12];
    int bytesRead = mdb_read_state(ftdi, buf, 11);
    while (bytesRead != 2) //TODO: READ THIS NUMBER FROM FILE.
    {
        bytesRead = mdb_read_state(ftdi, buf, 11);
    }

    //Printing results:
    int nameInd = 0;
    for (int i = 0; i < 8; i++)
    {
        char c = buf[i];
        char byteString[20];
        bin(c, byteString);
        for (int j = 0; j < strlen(byteString); j++)
        {
            int currNameLen = strlen(names[nameInd]);
            printf("%s:", names[nameInd]);
            for (int k = 0; k < MAX_NAME_LENGTH - currNameLen; k++)
                printf(" ");
            printf("%c\n", byteString[j]);
            nameInd++;
            if (nameInd == numNames)
            {
                printf("\n\n");
                return;
            }
        }
    }
}

int mdb_close(struct ftdi_context* ftdi)
{
    int ret;
    if ((ret = ftdi_usb_close(ftdi)) < 0)
    {
        fprintf(stderr, "unable to close ftdi device: %d (%s)\n", ret, ftdi_get_error_string(ftdi));
        ftdi_free(ftdi);
        return -1;
    }
    ftdi_free(ftdi);
    return 0;
}

int read_names(char** names)
{
    FILE * fp;
    char * line = NULL;
    size_t len = 0;
    ssize_t read;

    fp = fopen("names.txt", "r");
    if (fp == NULL)
        exit(EXIT_FAILURE);

    int numNames = 0;
    int l = 0;
    while ((read = getline(&line, &len, fp)) != -1) {
        names[numNames] = (char*)malloc(read);
        strcpy(names[numNames], line);
        l = strlen(names[numNames]);
        names[numNames][l-1] = '\0';
        printf("%s\n", names[numNames]);
        numNames++;
    }
    fclose(fp);
    if (line)
        free(line);

    return numNames;
}

void free_names(char** names, int numNames)
{
    for (int i = 0; i < numNames; i++)
    {
        free(names[i]);
    }
}

int main(int argc, char *argv[])
{
    struct ftdi_context* ftdi;
    if (mdb_init(&ftdi) < 0)
        return EXIT_FAILURE;
    int counter = 0;
    char *names[MAX_BITS_TRACKED]; //todo: make this dynamically sized
    int numNames = read_names((char**)names);
    for (int i = 0; i < numNames; i++)
    {
        printf("%s\n", names[i]);
    }

    while (1)
    {
        int rc;
        char buff[10];

        rc = getLine ("mdb -> ", buff, sizeof(buff));

        if (strcmp(buff, "s") == 0 ||  strcmp(buff, "step") == 0)
        {
            mdb_step(ftdi, names, numNames);
            printf("\n");
        }
        counter++;
    }
    mdb_close(ftdi);
    free_names((char**)names, numNames);
    return EXIT_SUCCESS;
}
