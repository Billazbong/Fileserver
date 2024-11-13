#pragma once

#include <stddef.h>
#include <stdlib.h>

#define MAX_LEN 1024
typedef struct {
    char buffer[MAX_LEN];
    size_t len;
    size_t cap;
} Buffer;

static inline void init_with_capacity(Buffer* self, size_t cap) {
    self->len = 0;
    self->cap = cap;
}