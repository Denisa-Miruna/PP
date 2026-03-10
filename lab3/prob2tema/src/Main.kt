import java.io.File

fun main() {

    val inputFile = File("ebook.txt")
    var text = inputFile.readText()
    text = text.replace(Regex("\\s\\d+\\s"), "")
    text = text.replace(Regex(" +"), " ")
    text = text.replace(Regex("\n+"), "\n")
    File("ebook_curat.txt").writeText(text)

}