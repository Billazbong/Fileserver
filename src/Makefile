CC = gcc
CFLAGS = -Iinclude -Wall -g
LDFLAGS = -levent

UNAME := $(shell uname)
ifeq ($(UNAME), Darwin) 
    CFLAGS += -I/opt/homebrew/include
    LDFLAGS += -L/opt/homebrew/lib
else ifeq ($(UNAME), Linux)
    CFLAGS += -I/usr/include
    LDFLAGS += -L/usr/lib
endif

SRC = server.c ip_helper.c
OBJ = $(SRC:.c=.o)
TARGET = server

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(OBJ) -o $(TARGET) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)