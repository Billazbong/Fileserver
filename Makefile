CC = gcc
CFLAGS = -Iinclude -Wall -g
LDFLAGS = -levent

UNAME := $(shell uname)
ARCH := $(shell uname -m)

ifeq ($(UNAME), Darwin)
    ifeq ($(ARCH), arm64)
        CFLAGS += -I/opt/homebrew/include
        LDFLAGS += -L/opt/homebrew/lib
    else ifeq ($(ARCH), x86_64)
        CFLAGS += -I/usr/local/include
        LDFLAGS += -L/usr/local/lib
    endif
else ifeq ($(UNAME), Linux)
    CFLAGS += -I/usr/include
    LDFLAGS += -L/usr/lib
endif

SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin
INCLUDE_DIR = include

SRC = $(wildcard $(SRC_DIR)/*.c)
OBJ = $(SRC:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)
TARGET = $(BIN_DIR)/server

all: $(TARGET)

$(TARGET): $(OBJ)
	mkdir -p $(BIN_DIR)
	$(CC) $(OBJ) -o $(TARGET) $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	mkdir -p $(OBJ_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJ_DIR) $(BIN_DIR)
