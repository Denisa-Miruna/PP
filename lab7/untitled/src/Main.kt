import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter


class HistoryLogRecord(
    val timestamp: OffsetDateTime,
    val commandLine: String       // ex: "SUBDEBUG Installed: qt5-..."
) : Comparable<HistoryLogRecord> {

    override fun compareTo(other: HistoryLogRecord): Int =
        this.timestamp.compareTo(other.timestamp)

    override fun equals(other: Any?): Boolean {
        if (other !is HistoryLogRecord) return false
        return this.timestamp == other.timestamp && this.commandLine == other.commandLine
    }

    override fun hashCode(): Int = 31 * timestamp.hashCode() + commandLine.hashCode()

    override fun toString(): String = "[$timestamp] $commandLine"
}

// Funcție  pentru maxim

fun <T : Comparable<T>> maxOf(a: T, b: T): T = if (a >= b) a else b

// 3. cauta o val si returneaza cheia


fun <K, V : Comparable<V>> findInProjection(
    target: V,
    source: Map<K, out V>
): K? = source.entries.find { it.value == target }?.key

// 4. Funcție de căutare și înlocuire

fun searchAndReplaceGeneric(
    target: HistoryLogRecord,
    replacement: HistoryLogRecord,
    map: MutableMap<OffsetDateTime, HistoryLogRecord>
) {
    val key: OffsetDateTime? = findInProjection(target, map)

    if (key != null) {
        map[key] = replacement
        println("  Inlocuit cu succes!")
        println("    Vechi: $target")
        println("    Nou:   $replacement")
    } else {
        println("  Obiectul nu a fost gasit in map.")
    }
}

 
// 5. Parsarea fișierului /var/log/dnf.rpm.log
 

fun parseDnfRpmLog(filePath: String): MutableMap<OffsetDateTime, HistoryLogRecord> {
    val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ssZ")
    val lines = java.io.File(filePath).readLines()
        .filter { it.isNotBlank() }
        .takeLast(50)

    val resultMap: MutableMap<OffsetDateTime, HistoryLogRecord> = mutableMapOf()

    for (line in lines) {
        val parts = line.split(" ", limit = 2)
        if (parts.size < 2) continue

        try {
            val timestamp = OffsetDateTime.parse(parts[0], formatter)
            val command = parts[1].trim()
            val record = HistoryLogRecord(timestamp, command)
            // Dacă există deja cheia (același timestamp), adăugăm un nanosecond
            var key = timestamp
            while (resultMap.containsKey(key)) key = key.plusNanos(1)
            resultMap[key] = record
        } catch (e: Exception) {
            println("Eroare la linia: $line") // debug
            continue
        }
    }

    return resultMap
}



fun main() {

    val logMap = parseDnfRpmLog("/var/log/dnf.rpm.log")
    println("Am citit ${logMap.size} inregistrari (ultimele 50):\n")
    logMap.values.forEachIndexed { i, r -> println("  ${i + 1}. $r") }

    val records = logMap.values.toList()

    // --- maxOf: cel mai recent dintre primele două ---
    println("\n--- maxOf: cel mai recent dintre primele doua inregistrari ---")
    if (records.size >= 2) {
        val max = maxOf(records[0], records[1])
        println("  Cel mai recent: $max")
    }

    // --- Căutare și înlocuire ---
    println("\n--- Cautare si inlocuire ---")
    if (records.size >= 3) {
        val target = records[2]
        val replacement = HistoryLogRecord(
            timestamp = target.timestamp,
            commandLine = "SUBDEBUG INLOCUIT: pachet-test-1.0.x86_64"
        )
        println("  Cautam: $target")
        searchAndReplaceGeneric(target, replacement, logMap)
    }

    // --- Sortare crescătoare după timestamp ---
    println("\n--- Primele 5 inregistrari sortate crescator dupa timestamp ---")
    logMap.values.sorted().take(5).forEach { println("  $it") }

    // --- Filtrare Installed ---
    println("\n--- Doar inregistrarile 'Installed' (primele 5) ---")
    logMap.values.filter { it.commandLine.contains("Installed:") }
        .take(5).forEach { println("  $it") }

    // --- Filtrare Erased/Removed ---
    println("\n--- Doar inregistrarile 'Erased'/'Removed' ---")
    val erased = logMap.values.filter {
        it.commandLine.contains("Erased:") || it.commandLine.contains("Removed:")
    }
    if (erased.isEmpty()) println("  (nicio inregistrare de stergere in ultimele 50)")
    else erased.take(5).forEach { println("  $it") }
}