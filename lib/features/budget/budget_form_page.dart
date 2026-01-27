import 'package:flutter/material.dart';
import '../../../core/models/budget_composition.dart';
import 'widgets/budget_calculator.dart';

class BudgetFormPage extends StatefulWidget {
  final Map<String, dynamic>? orcamentoExistente;

  const BudgetFormPage({super.key, this.orcamentoExistente});

  @override
  State<BudgetFormPage> createState() => _BudgetFormPageState();
}

class _BudgetFormPageState extends State<BudgetFormPage> {
  final _clienteCtrl = TextEditingController();
  final _ambienteCtrl = TextEditingController(text: 'Cozinha');

  double precoM2 = 0;
  double precoMLRodobanca = 0;
  double precoMLSaia = 0;
  double precoBojo = 0;
  double precoCooktop = 0;

  BancadaComposition? _composition;

  double get total {
    if (_composition == null) return 0;
    return _composition!.calcularTotal(
      precoM2: precoM2,
      precoMLRodobanca: precoMLRodobanca,
      precoMLSaia: precoMLSaia,
      precoBojo: precoBojo,
      precoCooktop: precoCooktop,
    );
  }

  void abrirCalculadora() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => BudgetCalculator(
          onConfirm: (composition) {
            setState(() => _composition = composition);
          },
        ),
      ),
    );
  }

  void salvarOrcamento() {
    if (_composition == null) return;

    final data = {
      'cliente': _clienteCtrl.text,
      'ambiente': _ambienteCtrl.text,
      'preco_m2': precoM2,
      'preco_ml_rodobanca': precoMLRodobanca,
      'preco_ml_saia': precoMLSaia,
      'total': total,
      'composicao': _composition!.toMap(
        precoM2: precoM2,
        precoMLRodobanca: precoMLRodobanca,
        precoMLSaia: precoMLSaia,
        precoBojo: precoBojo,
        precoCooktop: precoCooktop,
      ),
      'created_at': DateTime.now().toIso8601String(),
    };

    Navigator.pop(context, data);
  }

  Widget _campoDouble(String label, double valor, Function(double) onChanged) {
    return TextFormField(
      initialValue: valor == 0 ? '' : valor.toStringAsFixed(2),
      keyboardType: TextInputType.number,
      decoration: InputDecoration(labelText: label),
      onChanged: (v) => onChanged(double.tryParse(v) ?? 0),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Novo Orçamento')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _clienteCtrl,
            decoration: const InputDecoration(labelText: 'Cliente'),
          ),
          const SizedBox(height: 10),

          TextField(
            controller: _ambienteCtrl,
            decoration: const InputDecoration(labelText: 'Ambiente'),
          ),

          const Divider(height: 30),

          _campoDouble(
            'Preço do m² (R\$)',
            precoM2,
            (v) => setState(() => precoM2 = v),
          ),

          _campoDouble(
            'Preço ML Rodobanca (R\$)',
            precoMLRodobanca,
            (v) => setState(() => precoMLRodobanca = v),
          ),

          _campoDouble(
            'Preço ML Saia (R\$)',
            precoMLSaia,
            (v) => setState(() => precoMLSaia = v),
          ),

          const Divider(height: 30),

          ElevatedButton.icon(
            onPressed: abrirCalculadora,
            icon: const Icon(Icons.calculate),
            label: Text(
              _composition == null ? 'Adicionar Bancada' : 'Editar Bancada',
            ),
          ),

          if (_composition != null) ...[
            const SizedBox(height: 20),
            _ResumoBancada(composition: _composition!),
          ],

          const SizedBox(height: 30),

          Text(
            'Total: R\$ ${total.toStringAsFixed(2)}',
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),

          const SizedBox(height: 20),

          ElevatedButton(
            onPressed: salvarOrcamento,
            child: const Text('SALVAR ORÇAMENTO'),
          ),
        ],
      ),
    );
  }
}

class _ResumoBancada extends StatelessWidget {
  final BancadaComposition composition;

  const _ResumoBancada({required this.composition});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Bancada ${composition.tipo.name.toUpperCase()}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),

            ...composition.pecas.map(
              (p) => Text(
                '- ${p.nome}: '
                '${p.quantidade}x '
                '${p.comprimento} x ${p.largura} m '
                '| Área total ${p.areaTotal.toStringAsFixed(2)} m²',
              ),
            ),

            const SizedBox(height: 10),
            Text(
              'Rodobanca: ${composition.mlRodobancaTotal.toStringAsFixed(2)} m',
            ),
            Text('Saia: ${composition.mlSaiaTotal.toStringAsFixed(2)} m'),
          ],
        ),
      ),
    );
  }
}
