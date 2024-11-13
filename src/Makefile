# Makefile
CC = gcc
CFLAGS = -Iinclude -Wall -g
SRC = src/server.c src/ip_helper.c
OBJ = $(SRC:.c=.o)
TARGET = src/server

all: $(TARGET)

$(TARGET): $(OBJ)
	$(CC) $(OBJ) -o $(TARGET)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET)
