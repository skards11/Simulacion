# Auditoría final del manuscrito

- PDF: `manuscrito_final.pdf` (18 páginas totales).
- Cuerpo principal: páginas 1-14 (Referencias inician en la p. 14); Anexo inicia en la p. 15.
- Resumen: 228 palabras (rango 150-250).
- Términos prohibidos: {'anteproyecto': 0, 'provisional': 0, 'pendiente': 0}.
- Figuras a 300 dpi: {'fig_metricas_300dpi.png': (299.9994, 299.9994), 'fig_confusion_300dpi.png': (299.9994, 299.9994)}.
- Cifras contrastadas: 66; todas presentes: True.

## Cifras del manuscrito contra `outputs/`

| Afirmación | Valor | Redondeado | Fuente | Coincide |
|---|---:|---:|---|---|
| M0.macro_f1.mean | 0.660157 | 0.6602 | `models.M0.macro_f1.mean` | Sí |
| M0.macro_f1.sd | 0.026272 | 0.0263 | `models.M0.macro_f1.sd` | Sí |
| M0.macro_f1.min | 0.558121 | 0.5581 | `models.M0.macro_f1.min` | Sí |
| M0.macro_f1.max | 0.735584 | 0.7356 | `models.M0.macro_f1.max` | Sí |
| M0.macro_f1.ci_low | 0.608866 | 0.6089 | `models.M0.macro_f1.ci_low` | Sí |
| M0.macro_f1.ci_high | 0.712087 | 0.7121 | `models.M0.macro_f1.ci_high` | Sí |
| M0.accuracy.mean | 0.672849 | 0.6728 | `models.M0.accuracy.mean` | Sí |
| M0.accuracy.sd | 0.025665 | 0.0257 | `models.M0.accuracy.sd` | Sí |
| M0.accuracy.min | 0.596000 | 0.5960 | `models.M0.accuracy.min` | Sí |
| M0.accuracy.max | 0.744000 | 0.7440 | `models.M0.accuracy.max` | Sí |
| M0.accuracy.ci_low | 0.622000 | 0.6220 | `models.M0.accuracy.ci_low` | Sí |
| M0.accuracy.ci_high | 0.722050 | 0.7220 | `models.M0.accuracy.ci_high` | Sí |
| M0.recall_s3.mean | 0.673756 | 0.6738 | `models.M0.recall_s3.mean` | Sí |
| M0.recall_s3.sd | 0.065917 | 0.0659 | `models.M0.recall_s3.sd` | Sí |
| M0.recall_s3.min | 0.388889 | 0.3889 | `models.M0.recall_s3.min` | Sí |
| M0.recall_s3.max | 0.870229 | 0.8702 | `models.M0.recall_s3.max` | Sí |
| M0.recall_s3.ci_low | 0.539214 | 0.5392 | `models.M0.recall_s3.ci_low` | Sí |
| M0.recall_s3.ci_high | 0.789485 | 0.7895 | `models.M0.recall_s3.ci_high` | Sí |
| M1.macro_f1.mean | 0.660343 | 0.6603 | `models.M1.macro_f1.mean` | Sí |
| M1.macro_f1.sd | 0.021572 | 0.0216 | `models.M1.macro_f1.sd` | Sí |
| M1.macro_f1.min | 0.590747 | 0.5907 | `models.M1.macro_f1.min` | Sí |
| M1.macro_f1.max | 0.732360 | 0.7324 | `models.M1.macro_f1.max` | Sí |
| M1.macro_f1.ci_low | 0.616675 | 0.6167 | `models.M1.macro_f1.ci_low` | Sí |
| M1.macro_f1.ci_high | 0.702670 | 0.7027 | `models.M1.macro_f1.ci_high` | Sí |
| M1.accuracy.mean | 0.664486 | 0.6645 | `models.M1.accuracy.mean` | Sí |
| M1.accuracy.sd | 0.021137 | 0.0211 | `models.M1.accuracy.sd` | Sí |
| M1.accuracy.min | 0.584000 | 0.5840 | `models.M1.accuracy.min` | Sí |
| M1.accuracy.max | 0.738000 | 0.7380 | `models.M1.accuracy.max` | Sí |
| M1.accuracy.ci_low | 0.622000 | 0.6220 | `models.M1.accuracy.ci_low` | Sí |
| M1.accuracy.ci_high | 0.706000 | 0.7060 | `models.M1.accuracy.ci_high` | Sí |
| M1.recall_s3.mean | 0.698928 | 0.6989 | `models.M1.recall_s3.mean` | Sí |
| M1.recall_s3.sd | 0.042960 | 0.0430 | `models.M1.recall_s3.sd` | Sí |
| M1.recall_s3.min | 0.535714 | 0.5357 | `models.M1.recall_s3.min` | Sí |
| M1.recall_s3.max | 0.838710 | 0.8387 | `models.M1.recall_s3.max` | Sí |
| M1.recall_s3.ci_low | 0.611099 | 0.6111 | `models.M1.recall_s3.ci_low` | Sí |
| M1.recall_s3.ci_high | 0.783027 | 0.7830 | `models.M1.recall_s3.ci_high` | Sí |
| M2.macro_f1.mean | 0.498924 | 0.4989 | `models.M2.macro_f1.mean` | Sí |
| M2.macro_f1.sd | 0.029203 | 0.0292 | `models.M2.macro_f1.sd` | Sí |
| M2.macro_f1.min | 0.368634 | 0.3686 | `models.M2.macro_f1.min` | Sí |
| M2.macro_f1.max | 0.601859 | 0.6019 | `models.M2.macro_f1.max` | Sí |
| M2.macro_f1.ci_low | 0.437983 | 0.4380 | `models.M2.macro_f1.ci_low` | Sí |
| M2.macro_f1.ci_high | 0.555827 | 0.5558 | `models.M2.macro_f1.ci_high` | Sí |
| M2.accuracy.mean | 0.512347 | 0.5123 | `models.M2.accuracy.mean` | Sí |
| M2.accuracy.sd | 0.028843 | 0.0288 | `models.M2.accuracy.sd` | Sí |
| M2.accuracy.min | 0.396000 | 0.3960 | `models.M2.accuracy.min` | Sí |
| M2.accuracy.max | 0.612000 | 0.6120 | `models.M2.accuracy.max` | Sí |
| M2.accuracy.ci_low | 0.453950 | 0.4540 | `models.M2.accuracy.ci_low` | Sí |
| M2.accuracy.ci_high | 0.570000 | 0.5700 | `models.M2.accuracy.ci_high` | Sí |
| M2.recall_s3.mean | 0.490807 | 0.4908 | `models.M2.recall_s3.mean` | Sí |
| M2.recall_s3.sd | 0.071712 | 0.0717 | `models.M2.recall_s3.sd` | Sí |
| M2.recall_s3.min | 0.134146 | 0.1341 | `models.M2.recall_s3.min` | Sí |
| M2.recall_s3.max | 0.733333 | 0.7333 | `models.M2.recall_s3.max` | Sí |
| M2.recall_s3.ci_low | 0.341764 | 0.3418 | `models.M2.recall_s3.ci_low` | Sí |
| M2.recall_s3.ci_high | 0.622700 | 0.6227 | `models.M2.recall_s3.ci_high` | Sí |
| M0_vs_M1.mean_difference | -0.000186 | -0.0002 | `comparisons.M0_vs_M1.mean_difference` | Sí |
| M0_vs_M1.p_value_holm | 0.778031 | 0.7780 | `comparisons.M0_vs_M1.p_value_holm` | Sí |
| M0_vs_M1.cliff_delta | -0.006000 | -0.0060 | `comparisons.M0_vs_M1.cliff_delta` | Sí |
| M0_vs_M2.mean_difference | 0.161232 | 0.1612 | `comparisons.M0_vs_M2.mean_difference` | Sí |
| M0_vs_M2.p_value_holm | 0.000000 | 0.0000 | `comparisons.M0_vs_M2.p_value_holm` | Sí |
| M0_vs_M2.cliff_delta | 1.000000 | 1.0000 | `comparisons.M0_vs_M2.cliff_delta` | Sí |
| M0.confusion.diag1 | 0.800985 | 0.8010 | `models.M0.confusion_matrix_normalized[0][0]` | Sí |
| M0.confusion.diag2 | 0.514844 | 0.5148 | `models.M0.confusion_matrix_normalized[1][1]` | Sí |
| M0.confusion.diag3 | 0.676570 | 0.6766 | `models.M0.confusion_matrix_normalized[2][2]` | Sí |
| M2.confusion.diag1 | 0.594162 | 0.5942 | `models.M2.confusion_matrix_normalized[0][0]` | Sí |
| M2.confusion.diag2 | 0.426069 | 0.4261 | `models.M2.confusion_matrix_normalized[1][1]` | Sí |
| M2.confusion.diag3 | 0.492345 | 0.4923 | `models.M2.confusion_matrix_normalized[2][2]` | Sí |

## Hashes SHA-256

| Archivo | SHA-256 |
|---|---|
| `experimento_hmm_resumen.json` | `2bad64f61c416aefdad53298f62e4de9e93e8639918ef6b93558daec1860d289` |
| `tabla_resumen_manuscrito.csv` | `c5cee3deaf67d73cf25a03d79bfd7bbbfec1d46a8d23f8c7dcdc525c841900f9` |
| `fig_metricas_300dpi.png` | `c66038cba94d677247131c7c8a0b5530aa13c3074ecaa9ecbb693b833590ce54` |
| `fig_confusion_300dpi.png` | `bfd7329c55d118ea96b4b6fa348c5f0783797a553faca4c5bf713e84f211b1a0` |
