# A note about the header files

The .h files for this project contain all the working code, not just declarations. This is due to the nature of the Arduino environment. Many Arduino specific functions are automatically placed in the global scope by the compiler, and it handles .ino files differently than other files. Therefore, putting the code into the .h files is the cleanest and simplest way to include my own code from separate files.
