import 'package:flutter/material.dart';

// Imports absolutos para evitar erros de URI
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';
import 'sidebar.dart';

class LayoutBase extends StatefulWidget {
  final Widget child;
  final String titulo;
  final String? subtitulo;

  const LayoutBase({
    super.key,
    required this.child,
    this.titulo = 'Central Granitos',
    this.subtitulo,
  });

  @override
  State<LayoutBase> createState() => _LayoutBaseState();
}

class _LayoutBaseState extends State<LayoutBase> {
  bool conectado = true;

  @override
  void initState() {
    super.initState();
    _checarConexao();
  }

  // CORREÇÃO: verificarConexao() retorna um Future, então precisamos de um método async
  Future<void> _checarConexao() async {
    final status = await FirebaseService.verificarConexao();
    if (mounted) {
      setState(() {
        conectado = status;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool ehMobile = MediaQuery.of(context).size.width < 768;

    final viewWrapper = AnimatedOpacity(
      opacity: 1,
      duration: const Duration(milliseconds: 300),
      child: Padding(
        padding: EdgeInsets.all(ehMobile ? 20 : 30),
        child: widget.child,
      ),
    );

    // 📱 MOBILE
    if (ehMobile) {
      return Scaffold(
        backgroundColor: COLOR_BACKGROUND,
        appBar: AppBar(
          backgroundColor: COLOR_PRIMARY,
          elevation: 0,
          centerTitle: true,
          leading: Builder(
            builder: (context) => IconButton(
              icon: const Icon(Icons.menu_rounded, color: COLOR_WHITE),
              onPressed: () => Scaffold.of(context).openDrawer(),
            ),
          ),
          title: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                widget.titulo,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: COLOR_WHITE,
                ),
              ),
              if (widget.subtitulo != null)
                Text(
                  widget.subtitulo!,
                  style: const TextStyle(fontSize: 11, color: COLOR_WHITE),
                ),
            ],
          ),
        ),
        // CORREÇÃO: Passando os parâmetros obrigatórios que você definiu na Sidebar
        drawer: Drawer(
          child: Sidebar(
            userRole: "admin", // Depois integramos com o AuthController
            currentRoute: ModalRoute.of(context)?.settings.name ?? '',
            isMobile: true,
            onLogout: () {},
          ),
        ),
        body: Column(
          children: [
            if (!conectado)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                color: COLOR_WARNING,
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.wifi_off, size: 14, color: Colors.black87),
                    SizedBox(width: 5),
                    Text(
                      'TRABALHANDO OFFLINE',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.black87),
                    ),
                  ],
                ),
              ),
            Expanded(child: viewWrapper),
          ],
        ),
      );
    }

    // 🖥️ DESKTOP
    return Scaffold(
      backgroundColor: COLOR_BACKGROUND,
      body: Row(
        children: [
          // CORREÇÃO: Sidebar agora recebe os parâmetros necessários
          Sidebar(
            userRole: "admin", 
            currentRoute: ModalRoute.of(context)?.settings.name ?? '',
            onLogout: () {},
          ),
          Expanded(
            child: Column(
              children: [
                Expanded(child: viewWrapper),
              ],
            ),
          ),
        ],
      ),
    );
  }
}