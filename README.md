# Simple Imperative Language Compiler

## Author
Adam Bydłowski

## Description
This project was developed as part of the Formal Languages and Translation Techniques course at Wrocław University of Science and Technology.

It is a compiler for a basic imperative language that converts source code into virtual machine instructions. The compiler supports variables, arrays, procedures, fundamental arithmetic operations, and control structures like loops and conditional statements.

## Project Structure

The project consists of the following files in the compiler directory:

`lexer.py` – a lexical analyzer that splits the source code into tokens.\
`parser.py` – a syntax analyzer that constructs a simple syntax tree from tokens, represented as nested tuples.\
`codeGenerator.py` – a module that generates the final code for the virtual machine based on the tree constructed by the parser.\
`compiler.py` – the main file that initiates the entire compilation process.

## Additional directories and files
All the following directories and files were prepared by the course instructor, Dr. Maciej Gębala.

`kompilator-przyklady/testy` directory – example programs for verifying the correctness of the generated code.\
`kompilator-przyklady/program .. .imp` programs – additional utility scripts.\
`kompilator-przyklady/program .. .mr` programs – results of program .. .imp compilation.\
`kompilator-przyklady/maszyna_wirtualna` directory – virtual machine code.\
`kompilator-przyklady/gramatyka.txt` – grammar of the imperative language.\
`labor4.pdf` – project specification.

## Installation and usage

### Requirements

- Python 3.10 (`sudo apt install python3.10`)
- Python's `sly` package (`pip install sly`)

### Compilation

To compile the program, run the compiler from the terminal:

```sh
python3 compiler.py <input_file> <output_file>
```

where:
- `<input_file>` – the name of the file containing the source code in the imperative language,
- `<output_file>` – the name of the file where the generated virtual machine code will be saved.

## Notes

In the example6.imp file, the variable 'j' should be removed from the program declaration due to overloading (it is used as an iterator in the program).\
In the example8.imp file, on line 25, the array name 'tab' should be replaced with the correct name 't'.
