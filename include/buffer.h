#pragma once

#include <stddef.h>
#include <stdlib.h>

#include "constants.h"

/**
 * @brief A dynamic buffer structure.
 *
 * Holds a buffer of characters and information about its length and capacity.
 */
typedef struct {
    char *buffer;   /**< Pointer to the character buffer. */
    size_t len;     /**< Current length of the buffer. */
    size_t cap;     /**< Capacity of the buffer. */
} Buffer;

/**
 * @brief Initializes a Buffer structure with a given capacity.
 *
 * @param self A pointer to the Buffer structure to initialize.
 * @param cap The desired capacity.
 */
static inline void init_with_capacity(Buffer* self, size_t cap) {
    self->buffer = malloc(MAX_LEN);
    self->len = 0;
    self->cap = cap;
}
