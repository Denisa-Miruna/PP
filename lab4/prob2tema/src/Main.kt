import java.util.Scanner

data class Movie(
    val id: Int,
    val title: String,
    val seats: MutableList<Seat>
)

data class Seat(
    val row: Char,
    val number: Int,
    val price: Double
)



interface PaymentMethod {
    fun pay(amount: Double): Boolean
}

data class BankAccount(
    val cardNumber: String,
    val owner: String,
    var balance: Double
)

class CashPayment(private var money: Double) : PaymentMethod {

    override fun pay(amount: Double): Boolean {

        if (money >= amount) {
            money -= amount
            println("Plata cash efectuata.")
            return true
        }

        println("Bani insuficienti.")
        return false
    }
}

class CardPayment(private val account: BankAccount) : PaymentMethod {

    override fun pay(amount: Double): Boolean {

        if (account.balance >= amount) {
            account.balance -= amount
            println("Plata cu cardul efectuata.")
            return true
        }

        println("Fonduri insuficiente.")
        return false
    }
}


fun main() {

    val scanner = Scanner(System.`in`)

    val movies = mutableListOf(

        Movie(
            1,
            "Interstellar",
            mutableListOf(
                Seat('A',1,25.0),
                Seat('A',2,25.0),
                Seat('B',1,35.0)
            )
        ),

        Movie(
            2,
            "Inception",
            mutableListOf(
                Seat('A',1,25.0),
                Seat('A',2,25.0),
                Seat('B',1,35.0)
            )
        ),

        Movie(
            3,
            "Joker",
            mutableListOf(
                Seat('A',1,25.0),
                Seat('A',2,25.0),
                Seat('B',1,35.0)
            )
        )
    )

    var running = true

    while(running){

        println("\nFILME DISPONIBILE")

        movies.forEach {
            println("${it.id}. ${it.title}")
        }

        println("0. Iesire")

        print("Alege film: ")
        val filmId = scanner.nextInt()

        if(filmId == 0){
            running = false
            continue
        }

        val movie = movies.find { it.id == filmId }

        if(movie == null){
            println("Film invalid")
            continue
        }

        if(movie.seats.isEmpty()){
            println("Nu mai sunt locuri la acest film.")
            continue
        }

        println("\nLocuri disponibile:")

        movie.seats.forEachIndexed { index, seat ->
            println("${index+1}. ${seat.row}${seat.number} - ${seat.price} RON")
        }

        print("Alege loc: ")
        val seatIndex = scanner.nextInt() - 1

        val seat = movie.seats.getOrNull(seatIndex)

        if(seat == null){
            println("Loc invalid")
            continue
        }

        val price = seat.price

        println("\nMetoda plata:")
        println("1. Cash")
        println("2. Card")

        val option = scanner.nextInt()

        val payment: PaymentMethod

        if(option == 1){

            print("Suma cash: ")
            val money = scanner.nextDouble()

            payment = CashPayment(money)

        } else {

            scanner.nextLine()

            print("Numar card: ")
            val card = scanner.nextLine()

            print("Titular: ")
            val name = scanner.nextLine()

            print("Sold: ")
            val balance = scanner.nextDouble()

            val account = BankAccount(card,name,balance)

            payment = CardPayment(account)
        }

        println("\nProcesare plata...")

        if(payment.pay(price)){

            movie.seats.remove(seat)

            println("Bilet cumparat: ${movie.title} loc ${seat.row}${seat.number}")
        }
        else{
            println("Plata esuata.")
        }
    }
}