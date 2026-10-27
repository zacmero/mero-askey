# Askey RTV9015VW — source index

Checked **2026-10-26**. These are external references, not measurements from Zac's router. Do not turn a published same-model finding into a local result.

## Primary exact-model investigation

**O3 Labs — Askey RTV9015VW**

https://www.tripleoxygen.net/wiki/modem/rtv9015vw

The retrieved page reports this other-unit hardware:

| Role | Reported part/detail |
| --- | --- |
| SoC / bootloader family | Realtek RTL8685SF / RTL867X |
| Flash | Macronix MX25L6406E, 8 MB |
| Wireless | RTL8192ER, 2.4 GHz b/g/n |
| DSL component | RTL8275 |
| Telephone interface | Le9641PQC |
| USB / serial / JTAG | No USB; serial reported; JTAG unspecified |

For older firmware, it describes `/padrao`, `support` with the device-label admin password, and configuration download via `/saveconf.htm`. It describes editing `ENABLE_ADVANCE_PAGE` and `PADRAO_WIFI_ONLY` in `config.img`, importing it and rebooting. The page also reports updated firmware removing the straightforward Saveconf/DDNS pages.

**Applicability:** this establishes useful management and hardware leads, not a demonstrated root-shell recipe for Zac's firmware. A retrieved configuration is not a full flash backup. The described import/reboot is a persistent procedure to evaluate later, not an authorized first experiment.

## Earlier secondary tutorial — retrieval incomplete

Academia Técnica, earlier conversation link:

https://www.academiatecnica.com.br/2021/03/19/como-liberar-o-modo-de-configuracao-avancada-no-modem-adsl-askey/

This URL could not be retrieved in the publication session. It is preserved as a **location lead only**, not counted as independent verification of the method. Prefer the primary O3 Labs record above.

## Project-specific evidence

The owner's earlier enclosure-label photos identify RTV9015VW and were transcribed as 12 V DC / 1 A, manufactured 12/2018. No Askey internal-board photographs, exact firmware string, live service scan, serial log or shell output were supplied in this initialization session. No CPU ABI, RAM capacity, flash package, UART pin mapping or recovery mode is locally established.

The [MitraStar hardware report](https://github.com/zacmero/mero-mitrastar/blob/master/docs/experiments/mitra-hardware-020.md) explains the shared equipment limitations. Its chip, account, voltage and header observations do not belong to this Askey.

## Source questions for the next actual session

First capture this router's exact software/build and management behavior. Then search that build for an original firmware/source release or matching documented service behavior. Record the source date, model/revision, applicability and whether the text was actually retrieved. No matching image, OpenWrt installation path or network-to-shell method has been verified by this handoff.
