import discord
from discord.ext import commands
from discord.ext.commands import Context


def operator_logic(operator: chr, a: float | int, b: float | int) -> float | int:
    """Match operator and two values and compute the correct basic math function

    Args:
        operator (chr): a given basic mathematic operator
        a (float | int): first number 
        b (float | int): second number

    Returns:
        (flaot | int): The resulting value from the operation based on the operator
    """
    match operator:
        case '+':
            return a + b
        case '-':
            return a - b
        case '*':
            return a * b
        case '/':
            if b != 0:
                return a / b
        case '^':
            return a ** b
        case _:
            return None

def isFloat(num) -> bool:
    """Checks if a number is a float

    Args:
        num (_type_): input number to check

    Returns:
        bool: true if can be a float, otherwise false
    """
    try:
        float(num)
        return True
    except ValueError:
        return False

def tokenize(expression: str) -> list[str]:
    """Takes a string and tokenizes into list of string containing math numbers and simple operations

    Args:
        s (str): initial input string

    Returns:
        list[str]: tokenized result of the input in proper form for math
    """
    VALID_NUMBERS = set[str]("0123456789.")
    tokens = []
    current_number = []
    prev_char = None

    for char in expression:
        if char.isspace():
            continue
        if char == '-':
            if current_number:
                tokens.append(''.join(current_number))
                current_number = []
            if prev_char in ('(', '-', '+', '*', '/', '^', None):
                tokens.append('0')
            tokens.append('-')
        elif char in VALID_NUMBERS:
            current_number.append(char)
        else:
            if current_number:
                tokens.append(''.join(current_number))
                current_number = []
            tokens.append(char)
        
        prev_char = char
    if current_number:
        tokens.append(''.join(current_number))
    return tokens

def evaluate(tokens: list[str]) -> float | int:
    """Evaluate a list of string of math according to order of operations: {()} > {^} > {*,/} > {+,-}

    Fun Fact: This logic function was created by me after my Meta Coding Interview where I had to solve this problem (though a bit simpler)

    Args:
        tokens (list[str]): List of tokenized strings ready to be evaluated as a math equation

    Returns:
        float: Single value being the resulting solution from the math equation
    """
    priority = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3,
    }

    output_stack = []
    operator_stack = []

    for token in tokens:
        if token.isdigit():
            output_stack.append(int(token)) # Prefer using ints over floats whenever possible
        elif isFloat(token):
            output_stack.append(float(token))
        elif token in priority:
            while operator_stack and operator_stack[-1] != '(' and priority.get(operator_stack[-1], 0) >= priority.get(token, 0):
                b = output_stack.pop()
                a = output_stack.pop()
                output_stack.append(operator_logic(operator_stack.pop(), a, b))
            operator_stack.append(token)
        elif token == '(':
            operator_stack.append('(')
        elif token == ')':
            while operator_stack[-1] != '(':
                b = output_stack.pop()
                a = output_stack.pop()
                output_stack.append(operator_logic(operator_stack.pop(), a, b))
            operator_stack.pop() # Remove the '(' from the operator stack
        else:
            raise ValueError(f"Invalid token: {token}")
    while operator_stack:
        b = output_stack.pop()
        a = output_stack.pop()
        output_stack.append(operator_logic(operator_stack.pop(), a, b))
    return output_stack.pop()

def calculate_expression(expression: str, precision: int = 2) -> float | int:
    """
    :type s: str
    :type precision: int
    :rtype: float or int
    """
    tokens = tokenize(expression)
    result = evaluate(tokens)
    return round(result, precision)


class Calculator(commands.Cog, name="Calculator"):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="calculate",
        description="Computes the result of a mathematical expression."
    )
    @discord.app_commands.describe(
        expression="The mathematical expression to calculate",
        precision="The number of decimal places to round the result to (optonal, default: 2)"
    )
    async def calculate(self, context: Context, expression: str, precision: int = 2) -> None:
        """
        Computes the result of a mathematical expression.
        """
        try:
            embed = discord.Embed(
                title="**Calculator**",
                description=f"# ```{expression} = {calculate_expression(expression, precision=precision)}```",
                color=0x42F56C
            )
        except ValueError as e:
            embed = discord.Embed(
                title="**Error**",
                description=f"```Invalid Characters in your expression: {e}```",
                color=0xE02B2B
            )
        except Exception as e:
            embed = discord.Embed(
                title="**Error**",
                description=f"```{e}```",
                color=0xE02B2B
            )
        embed.set_footer(text=f"NOTE: If you want to use a negative number, you need to use parentheses. Example: (-1), repeated use of operators without parentheses will result in an error.")
        await context.send(embed=embed)

async def setup(bot) -> None:
    await bot.add_cog(Calculator(bot))