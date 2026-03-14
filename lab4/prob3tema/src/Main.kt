import java.io.File
import java.time.LocalDateTime
import java.util.Scanner


data class User(
    val name: String
)

data class Note(
    val author: String,
    val date: String,
    val content: String
)

class NoteManager(private val folder: String = "notes") {

    init {
        File(folder).mkdirs()
    }

    fun listNotes() {
        val files = File(folder).listFiles()

        if (files.isNullOrEmpty()) {
            println("Nu exista notite.")
            return
        }

        println("\nLista notite:")
        files.forEachIndexed { index, file ->
            println("${index + 1}. ${file.nameWithoutExtension}")
        }
    }

    fun createNote(user: User, title: String, content: String) {

        val date = LocalDateTime.now().toString()

        val note = Note(user.name, date, content)

        val file = File("$folder/$title.txt")

        file.writeText(
            "Autor: ${note.author}\n" +
                    "Data: ${note.date}\n\n" +
                    note.content
        )

        println("Notita salvata.")
    }

    fun loadNote(title: String) {

        val file = File("$folder/$title.txt")

        if (!file.exists()) {
            println("Notita nu exista.")
            return
        }

        println("\n--- NOTITA ---")
        println(file.readText())
    }

    fun deleteNote(title: String) {

        val file = File("$folder/$title.txt")

        if (file.exists()) {
            file.delete()
            println("Notita stearsa.")
        } else {
            println("Notita nu exista.")
        }
    }
}

fun main() {

    val scanner = Scanner(System.`in`)

    print("Introdu numele userului: ")
    val userName = scanner.nextLine()

    val user = User(userName)
    val manager = NoteManager()

    var running = true

    while (running) {

        println("\nMENIU")
        println("1. Afiseaza notite")
        println("2. Creeaza notita")
        println("3. Incarca notita")
        println("4. Sterge notita")
        println("0. Iesire")

        print("Alege optiune: ")

        when (scanner.nextLine()) {

            "1" -> manager.listNotes()

            "2" -> {
                print("Titlu notita: ")
                val title = scanner.nextLine()

                print("Continut: ")
                val content = scanner.nextLine()

                manager.createNote(user, title, content)
            }

            "3" -> {
                print("Titlu notita: ")
                val title = scanner.nextLine()

                manager.loadNote(title)
            }

            "4" -> {
                print("Titlu notita: ")
                val title = scanner.nextLine()

                manager.deleteNote(title)
            }

            "0" -> running = false

            else -> println("Optiune invalida")
        }
    }
}