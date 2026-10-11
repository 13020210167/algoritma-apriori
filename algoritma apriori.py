from itertools import combinations
from math import ceil

# ==========================================================
# IMPLEMENTASI ALGORITMA APRIORI
# Menghasilkan frequent itemsets dan aturan asosiasi
# ==========================================================

# 1. DATA TRANSAKSI
transaksi = [
    ["Roti", "Susu"],
    ["Bir", "Diapers", "Roti", "Telur"],
    ["Bir", "Cola", "Diapers", "Susu"],
    ["Bir", "Diapers", "Roti", "Susu"],
    ["Cola", "Diapers", "Roti", "Susu"]
]

# 2. PARAMETER
minimum_support = 40       # Dalam persen
minimum_confidence = 60    # Dalam persen


def hitung_support(itemset, transaksi):
    """Menghitung jumlah transaksi yang memuat itemset."""
    return sum(
        1 for tx in transaksi
        if set(itemset).issubset(set(tx))
    )


def apriori(transaksi, min_support, min_confidence):
    jumlah_transaksi = len(transaksi)

    if jumlah_transaksi == 0:
        raise ValueError("Data transaksi tidak boleh kosong.")

    if not 0 < min_support <= 100:
        raise ValueError("Minimum support harus antara 1-100.")

    if not 0 < min_confidence <= 100:
        raise ValueError("Minimum confidence harus antara 1-100.")

    # Mengubah transaksi menjadi set agar item tidak dihitung ganda
    transaksi = [set(tx) for tx in transaksi]

    # Ambang minimum jumlah transaksi
    batas_support = ceil(
        jumlah_transaksi * min_support / 100
    )

    # Menyimpan jumlah kemunculan setiap itemset
    support_count = {}

    # Mengumpulkan semua item unik
    semua_item = sorted(
        set(item for tx in transaksi for item in tx)
    )

    # ------------------------------------------------------
    # TAHAP 1: GENERATE DAN COUNT ITEMSET 1 (C1)
    # ------------------------------------------------------
    kandidat = [(item,) for item in semua_item]

    frequent_sebelumnya = []

    for itemset in kandidat:
        count = hitung_support(itemset, transaksi)
        support_count[itemset] = count

        if count >= batas_support:
            frequent_sebelumnya.append(itemset)

    frequent_semua = []
    level = 1

    print("\n=== PROSES ALGORITMA APRIORI ===")
    print(f"Jumlah transaksi  : {jumlah_transaksi}")
    print(f"Minimum support   : {min_support}%")
    print(f"Minimum confidence: {min_confidence}%")
    print(f"Batas support     : {batas_support} transaksi")

    # ------------------------------------------------------
    # TAHAP 2: GENERATE, PRUNE, COUNT, DAN SELECT
    # ------------------------------------------------------
    while frequent_sebelumnya:
        print(f"\nL{level}: Frequent {level}-itemset")

        for itemset in frequent_sebelumnya:
            count = support_count[itemset]
            support = count / jumlah_transaksi * 100

            frequent_semua.append(itemset)

            print(
                f"{itemset} | Count={count} | "
                f"Support={support:.2f}%"
            )

        # Membentuk kandidat untuk level berikutnya
        kandidat_berikutnya = set()
        panjang_baru = level + 1

        for i in range(len(frequent_sebelumnya)):
            for j in range(i + 1, len(frequent_sebelumnya)):
                gabungan = tuple(sorted(
                    set(frequent_sebelumnya[i])
                    | set(frequent_sebelumnya[j])
                ))

                # Kandidat harus memiliki panjang yang sesuai
                if len(gabungan) != panjang_baru:
                    continue

                # PRUNE: semua subset berukuran k harus frequent
                semua_subset_frequent = all(
                    tuple(subset) in frequent_sebelumnya
                    for subset in combinations(gabungan, level)
                )

                if semua_subset_frequent:
                    kandidat_berikutnya.add(gabungan)

        # COUNT dan SELECT kandidat berikutnya
        frequent_berikutnya = []

        for itemset in sorted(kandidat_berikutnya):
            count = hitung_support(itemset, transaksi)
            support_count[itemset] = count

            if count >= batas_support:
                frequent_berikutnya.append(itemset)

        print(
            f"Jumlah kandidat C{panjang_baru}: "
            f"{len(kandidat_berikutnya)}"
        )

        frequent_sebelumnya = frequent_berikutnya
        level += 1

    # ------------------------------------------------------
    # TAHAP 3: MEMBENTUK ATURAN ASOSIASI
    # ------------------------------------------------------
    aturan = []

    for itemset in frequent_semua:
        if len(itemset) < 2:
            continue

        count_gabungan = support_count[itemset]
        support_gabungan = count_gabungan / jumlah_transaksi

        # Membentuk semua kemungkinan sisi kiri aturan
        for ukuran in range(1, len(itemset)):
            for sisi_kiri in combinations(itemset, ukuran):
                sisi_kanan = tuple(
                    item for item in itemset
                    if item not in sisi_kiri
                )

                count_kiri = support_count.get(sisi_kiri, 0)
                count_kanan = support_count.get(sisi_kanan, 0)

                if count_kiri == 0 or count_kanan == 0:
                    continue

                # Confidence = support(X dan Y) / support(X)
                confidence = count_gabungan / count_kiri

                # Lift = confidence(X -> Y) / support(Y)
                support_kanan = count_kanan / jumlah_transaksi
                lift = confidence / support_kanan

                if confidence * 100 >= min_confidence:
                    aturan.append({
                        "kiri"      : sisi_kiri,
                        "kanan"     : sisi_kanan,
                        "support"   : support_gabungan * 100,
                        "confidence": confidence * 100,
                        "lift": lift
                    })

    # Urutkan aturan berdasarkan confidence, lift, lalu support
    aturan.sort(
        key=lambda x: (
            -x["confidence"],
            -x["lift"],
            -x["support"]
        )
    )

    return frequent_semua, aturan


# ==========================================================
# 4. MENJALANKAN PROGRAM
# ==========================================================
frequent_itemsets, aturan = apriori(
    transaksi,
    minimum_support,
    minimum_confidence
)

print("\n=== HASIL ATURAN ASOSIASI ===")

if aturan:
    for nomor, rule in enumerate(aturan, start=1):
        kiri = " + ".join(rule["kiri"])
        kanan = " + ".join(rule["kanan"])

        print(f"\nAturan {nomor}: {kiri} -> {kanan}")
        print(f"Support    : {rule['support']:.2f}%")
        print(f"Confidence : {rule['confidence']:.2f}%")
        print(f"Lift       : {rule['lift']:.2f}")

else:
    print("Tidak ada aturan yang memenuhi minimum confidence.")

print("\n=== RINGKASAN ===")
print(f"Jumlah transaksi       : {len(transaksi)}")
print(f"Jumlah item unik       : {len(set(item for tx in transaksi for item in tx))}")
print(f"Jumlah frequent itemset: {len(frequent_itemsets)}")
print(f"Jumlah aturan asosiasi  : {len(aturan)}")
