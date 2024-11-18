#pragma once

#include <stddef.h>
#include <stdlib.h>

#include "constants.h"

typedef struct {
    char *buffer;
    size_t len;
    size_t cap;
} Buffer;

static inline void init_with_capacity(Buffer* self, size_t cap) {
    self->buffer=malloc(MAX_LEN);
    self->len = 0;
    self->cap = cap;
}