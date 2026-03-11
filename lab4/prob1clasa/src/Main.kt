import kotlin.io.println

data class Content(private var author:String,
                   private var text: String,
                   private var name: String,
                   private var publisher:String,
                    private var price: Int)
                    //constructor implicit care initializeaza el valorile parametrilor
{
    fun setPrice(price :Int)
    {
        this.price = price
    }
    fun getPrice():Int
    {
        return this.price
    }
    fun getAuthor(): String
    {
        return author
    }
    fun setAuthor(author: String)
    {
        this.author= author
    }
    fun getText(): String
    {
        return text
    }
    fun setText(text:String)
    {
        this.text= text
    }
    fun getName(): String
    {
        return name
    }
    fun setNUme(name:String)
    {
        this.name= name
    }
    fun getPublisher(): String
    {
        return publisher
    }
    fun setPublisher(publisher:String)
    {
        this.publisher=publisher
    }
}

data class Book(private var data: Content)
{
    override fun toString():String
    {
        return "nume carte: "+ data.getName()+ " autor: "+data.getAuthor()+" pret: "+data.getPrice()
    }
    fun getName(): String=data.getName()
    fun getAuthor(): String= data.getAuthor()
    fun getPublisher(): String = data.getPublisher()
    fun getContent(): String=data.getText()
    fun hasAuthor(author: String): Boolean{
        return data.getAuthor() == author
    }
    fun hasTitle(title: String): Boolean
    {
        return data.getName() == title
    }
    fun isPublishedBy(publisher: String) : Boolean
    {
        return data.getPublisher()==publisher
    }
}

class Library()
{
    private var books: MutableSet<Book> = mutableSetOf()
    fun getBooks(): Set<Book>
    {
        return books
    }
    fun addBook(book :Book)
    {
        books.add(book)
    }
    fun findAllByAuthor(author: String):Set<Book>
    {
        var rez=mutableSetOf<Book>()
        for(book in books)
        {
            if(book.hasAuthor(author))
            {
                rez.add(book)
            }
        }
        return rez
    }
    fun findAllByName(name: String):Set<Book>
    {
        var rez=mutableSetOf<Book>()
        for(book in books)
        {
            if(book.hasTitle(name))
            {
                rez.add(book)
            }
        }
        return rez
    }
    fun findAllByPublisher(publisher: String):Set<Book>
    {
        var rez=mutableSetOf<Book>()
        for(book in books)
        {
            if(book.isPublishedBy(publisher))
            {
                rez.add(book)
            }
        }
        return rez
    }
}

interface LibraryPrinter
{
    fun print(books: Set<Book>)
}

interface formatDocument //principiul separarii inferfetelor
{
    fun printHeader()
    fun printFooter()
}

class BooksRaw :LibraryPrinter  //principiul dependentei inverse
{
    override fun print(books: Set<Book>)
    {
        for( book in books)
        {
            print("${book.toString()}\n")
        }
    }
}
class BooksHTML : LibraryPrinter , formatDocument{
    override fun printHeader() {
        println("<html><body><ul>")
    }
    override fun print(books: Set<Book>) {
        printHeader()
        for (book in books) {
            println("  <li>${book.toString()}</li>")
        }
        printFooter()
    }

    override fun printFooter() {
        println("</ul></body></html>")
    }
}
class BooksJSON : LibraryPrinter , formatDocument{
    override fun printHeader() {
        println("[")
    }
    override fun print(books: Set<Book>) {
        printHeader()

        for (book in books) {
            println("  { " +book.toString()+" } ")
        }
        printFooter()
    }
    override fun printFooter() {
        println("]")
    }
}
fun main() {
    val c1 = Content("Ion Creanga", "Era odata un moș...", "Amintiri", "Junimea", 23)
    val carte1 = Book(c1)

    val c2 = Content("Mihai Eminescu", "A fost odata...", "Luceafarul", "Junimea",33)
    val carte2 = Book(c2)

    val c3 = Content("Mircea Eliade", "In noaptea de...", "Maitreyi", "Humanitas",20)
    val carte3 = Book(c3)
    val bibliotecaMea=Library()
    bibliotecaMea.addBook(carte1)
    bibliotecaMea.addBook(carte2)
    bibliotecaMea.addBook(carte3)
    
    val printerRaw: LibraryPrinter = BooksRaw()
    printerRaw.print(bibliotecaMea.getBooks())


    val cartiJunimea = bibliotecaMea.findAllByPublisher("Junimea")
    val printerJson: LibraryPrinter = BooksJSON()
    printerJson.print(cartiJunimea)

    val printerHtml :LibraryPrinter= BooksHTML()
    printerHtml.print(bibliotecaMea.getBooks())
}