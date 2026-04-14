import java.util.*

// ─────────────────────────────────────────────
//  TOKEN
// ─────────────────────────────────────────────
sealed class Token {
    data class Num(val value: Double) : Token()
    data class Op(val ch: Char) : Token()
    object LParen : Token()
    object RParen : Token()
}

// ─────────────────────────────────────────────
//  TOKENIZER  →  String  ──►  List<Token>
// ─────────────────────────────────────────────
fun tokenize(expr: String): List<Token> {
    val tokens = mutableListOf<Token>()
    var i = 0
    while (i < expr.length) {
        when {
            expr[i].isWhitespace() -> i++

            // număr (inclusiv zecimal)
            expr[i].isDigit() || expr[i] == '.' -> {
                val sb = StringBuilder()
                while (i < expr.length && (expr[i].isDigit() || expr[i] == '.')) {
                    sb.append(expr[i++])
                }
                tokens += Token.Num(sb.toString().toDouble())
            }

            // minus unar: la început sau după '('
            expr[i] == '-' && (tokens.isEmpty() || tokens.last() is Token.LParen) -> {
                // tratăm ca  0 - ...
                tokens += Token.Num(0.0)
                tokens += Token.Op('-')
                i++
            }

            expr[i] == '(' -> { tokens += Token.LParen; i++ }
            expr[i] == ')' -> { tokens += Token.RParen; i++ }

            expr[i] in "+-*/" -> { tokens += Token.Op(expr[i]); i++ }

            else -> throw IllegalArgumentException("Caracter necunoscut: '${expr[i]}'")
        }
    }
    return tokens
}

// ─────────────────────────────────────────────
//  PRECEDENȚĂ & ASOCIATIVITATE
// ─────────────────────────────────────────────
fun precedence(op: Char) = when (op) {
    '+', '-' -> 1
    '*', '/' -> 2
    else     -> 0
}

fun isLeftAssoc(op: Char) = op in "+-*/"

// ─────────────────────────────────────────────
//  SHUNTING-YARD  →  infix  ──►  postfix (RPN)
//  Stivă EXPLICITĂ de operatori (Stack<Char>)
// ─────────────────────────────────────────────
fun toPostfix(tokens: List<Token>): List<Token> {
    val output  = mutableListOf<Token>()
    val opStack = Stack<Token>()   // stivă explicită

    for (token in tokens) {
        when (token) {
            is Token.Num -> output += token

            is Token.Op -> {
                // scoate operatori cu precedență mai mare (sau egală + left-assoc)
                while (opStack.isNotEmpty()
                    && opStack.peek() is Token.Op
                    && run {
                        val top = (opStack.peek() as Token.Op).ch
                        precedence(top) > precedence(token.ch)
                                || (precedence(top) == precedence(token.ch) && isLeftAssoc(token.ch))
                    }
                ) {
                    output += opStack.pop()
                }
                opStack.push(token)
            }

            is Token.LParen -> opStack.push(token)

            is Token.RParen -> {
                // golește până la '('
                while (opStack.isNotEmpty() && opStack.peek() !is Token.LParen) {
                    output += opStack.pop()
                }
                if (opStack.isEmpty())
                    throw IllegalArgumentException("Paranteză închisă fără pereche!")
                opStack.pop() // elimină '('
            }
        }
    }

    // mută operatorii rămași în output
    while (opStack.isNotEmpty()) {
        val top = opStack.pop()
        if (top is Token.LParen)
            throw IllegalArgumentException("Paranteză deschisă fără pereche!")
        output += top
    }

    return output
}

// ─────────────────────────────────────────────
//  EVALUARE POSTFIX
//  Stivă EXPLICITĂ de operanzi (Stack<Double>)
// ─────────────────────────────────────────────
fun evalPostfix(postfix: List<Token>): Double {
    val stack = Stack<Double>()   // stivă explicită

    for (token in postfix) {
        when (token) {
            is Token.Num -> stack.push(token.value)

            is Token.Op -> {
                if (stack.size < 2)
                    throw IllegalArgumentException("Expresie invalidă!")
                val b = stack.pop()
                val a = stack.pop()
                val res = when (token.ch) {
                    '+' -> a + b
                    '-' -> a - b
                    '*' -> a * b
                    '/' -> {
                        if (b == 0.0) throw ArithmeticException("Împărțire la zero!")
                        a / b
                    }
                    else -> throw IllegalArgumentException("Operator necunoscut: ${token.ch}")
                }
                stack.push(res)
            }

            else -> throw IllegalArgumentException("Token neașteptat în postfix!")
        }
    }

    if (stack.size != 1)
        throw IllegalArgumentException("Expresie malformată!")
    return stack.pop()
}

// ─────────────────────────────────────────────
//  FUNCȚIE PRINCIPALĂ DE EVALUARE
// ─────────────────────────────────────────────
fun evaluate(expr: String): Double {
    val tokens  = tokenize(expr)
    val postfix = toPostfix(tokens)
    return evalPostfix(postfix)
}

// ─────────────────────────────────────────────
//  MAIN  –  mod interactiv
// ─────────────────────────────────────────────
fun main() {
    println("=== Calculator cu Notație Poloneză (RPN) ===")
    println("Suportă: +  -  *  /  și paranteze")
    println("Exemple: 2*(4-5/6)/456   |   -3+4*(2-8)")
    println("Tastează 'exit' pentru a ieși.\n")

    val reader = Scanner(System.`in`)

    while (true) {
        print("Expresie: ")
        val input = reader.nextLine().trim()
        if (input.lowercase() == "exit") break
        if (input.isEmpty()) continue

        try {
            val tokens  = tokenize(input)
            val postfix = toPostfix(tokens)

            // afișează forma postfix (opțional, educativ)
            val postfixStr = postfix.joinToString(" ") { t ->
                when (t) {
                    is Token.Num -> if (t.value == t.value.toLong().toDouble())
                        t.value.toLong().toString() else t.value.toString()
                    is Token.Op  -> t.ch.toString()
                    else         -> "?"
                }
            }

            val result = evalPostfix(postfix)
            println("  Postfix : $postfixStr")
            println("  Rezultat: $result\n")

        } catch (e: Exception) {
            println("  Eroare: ${e.message}\n")
        }
    }

    println("La revedere!")
}