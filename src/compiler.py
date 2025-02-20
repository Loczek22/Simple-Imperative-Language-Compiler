import sys
from lexer import MajLexer
from parser import MajParser
from codeGenerator import CodeGenerator

    
def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compiler.py <in_file> <out_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    lexer = MajLexer()
    parser = MajParser()
    gen = CodeGenerator()
    
    try:
        with open(input_file, "r") as file:
            source_code = file.read()
        
        tokens = lexer.tokenize(source_code)
        parsed = parser.parse(tokens)
        gen.generate_all(parsed)
        
        with open(output_file, "w") as f:
            for i in gen.code:
                f.write(i+"\n")
        
        print(f"\nVirtual machine code saved to '{output_file}'.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()