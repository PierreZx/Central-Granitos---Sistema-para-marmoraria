import 'package:flutter/material.dart';
import '../../../core/models/budget_composition.dart';
import '../widgets/bancada_preview.dart';

class BudgetCalculator extends StatefulWidget {
  final Function(BancadaComposition) onConfirm;

  const BudgetCalculator({super.key, required this.onConfirm});

  @override
  State<BudgetCalculator> createState() => _BudgetCalculatorState();
}

class _BudgetCalculatorState extends State<BudgetCalculator>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late BancadaComposition composition;

  @override
  void initState() {
    super.initState();

    composition = BancadaComposition(
      tipo: BancadaTipo.reta,
      pecas: [BancadaPiece(nome: 'P1', comprimento: 1.0, largura: 0.6)],
    );

    _tabController = TabController(length: 3, vsync: this);
  }

  void _recalcularTipo() {
    setState(() {
      composition.tipo = composition.pecas.length == 1
          ? BancadaTipo.reta
          : composition.pecas.length == 2
          ? BancadaTipo.l
          : BancadaTipo.u;
    });
  }

  void confirmar() {
    widget.onConfirm(composition);
    Navigator.pop(context);
  }

  Widget _campoDouble(String label, double valor, Function(double) onChanged) {
    return TextFormField(
      initialValue: valor.toString(),
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label),
      onChanged: (v) => onChanged(double.tryParse(v) ?? 0),
    );
  }

  // =========================
  // ABA 1 — PEDRAS
  // =========================
  Widget _abaPedras() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: BancadaPreview(composition: composition),
        ),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              ...composition.pecas.map((p) {
                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          p.nome,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        _campoDouble(
                          'Comprimento (m)',
                          p.comprimento,
                          (v) => setState(() => p.comprimento = v),
                        ),
                        _campoDouble(
                          'Largura (m)',
                          p.largura,
                          (v) => setState(() => p.largura = v),
                        ),
                      ],
                    ),
                  ),
                );
              }),
              if (composition.pecas.length == 1)
                ElevatedButton(
                  onPressed: () {
                    setState(() {
                      composition.pecas.add(
                        BancadaPiece(
                          nome: 'P2',
                          comprimento: 1,
                          largura: 0.6,
                          ladoEncaixe: Side.direita,
                        ),
                      );
                      _recalcularTipo();
                    });
                  },
                  child: const Text('+ Bancada em L'),
                ),
              if (composition.pecas.length == 2)
                ElevatedButton(
                  onPressed: () {
                    setState(() {
                      composition.pecas.add(
                        BancadaPiece(
                          nome: 'P3',
                          comprimento: 1,
                          largura: 0.6,
                          ladoEncaixe: Side.esquerda,
                        ),
                      );
                      _recalcularTipo();
                    });
                  },
                  child: const Text('+ Bancada em U'),
                ),
            ],
          ),
        ),
      ],
    );
  }

  // =========================
  // ABA 2 — ACABAMENTOS
  // =========================
  Widget _abaAcabamentos() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: composition.pecas.map((p) {
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Acabamentos – ${p.nome}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 8),
                ...Side.values.map(
                  (side) => CheckboxListTile(
                    dense: true,
                    title: Text('Rodobanca ${side.name}'),
                    value: p.rodobanca[side],
                    onChanged: p.ladoEncaixe == side
                        ? null
                        : (v) => setState(() => p.rodobanca[side] = v ?? false),
                  ),
                ),
                const Divider(),
                ...Side.values.map(
                  (side) => CheckboxListTile(
                    dense: true,
                    title: Text('Saia ${side.name}'),
                    value: p.saia[side],
                    onChanged: p.ladoEncaixe == side
                        ? null
                        : (v) => setState(() => p.saia[side] = v ?? false),
                  ),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  // =========================
  // ABA 3 — BOJO / COOKTOP
  // =========================
  Widget _abaAberturas() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: composition.pecas.map((p) {
        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Aberturas – ${p.nome}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                SwitchListTile(
                  title: const Text('Possui Bojo'),
                  value: p.temBojo,
                  onChanged: (v) => setState(() => p.temBojo = v),
                ),
                SwitchListTile(
                  title: const Text('Possui Cooktop'),
                  value: p.temCooktop,
                  onChanged: (v) => setState(() => p.temCooktop = v),
                ),
              ],
            ),
          ),
        );
      }).toList(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Calculadora de Bancada'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Pedras'),
            Tab(text: 'Acabamentos'),
            Tab(text: 'Bojo / Cooktop'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [_abaPedras(), _abaAcabamentos(), _abaAberturas()],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: confirmar,
        icon: const Icon(Icons.check),
        label: const Text('Confirmar'),
      ),
    );
  }
}
