CC = gcc
CFLAGS = -Wall -O2 -pthread
LDFLAGS = -lssl -lcrypto -lpthread -lm
TARGET = raven_node
SRC = ../src/blockchain.c

all: $(TARGET)

$(TARGET): $(SRC)
$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

clean:
rm -f $(TARGET)

run: $(TARGET)
./$(TARGET)

.PHONY: all clean run
