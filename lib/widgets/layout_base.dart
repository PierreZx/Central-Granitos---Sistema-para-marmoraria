import 'package:flutter/material.dart';

import '../core/utils/constants.dart';
import '../features/widgets/sidebar.dart';
import '../core/services/firebase_service.dart';

class LayoutBase extends StatelessWidget {
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
  Widget build(BuildContext context) {
    final bool ehMobile = MediaQuery.of(context).size.width < 768;
    final bool conectado = FirebaseService.verificarConexao();

    // 🔹 Wrapper com padding + animação
    final viewWrapper = AnimatedOpacity(
      opacity: 1,
      duration: const Duration(milliseconds: 300),
      child: Padding(
        padding: EdgeInsets.all(ehMobile ? 20 : 30),
        child: child,
      ),
    );

    // 📱 MOBILE
    if (ehMobile) {
      return Scaffold(
        backgroundColor: COLOR_BACKGROUND,

        // 🟦 AppBar
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
                titulo,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: COLOR_WHITE,
                ),
              ),
              if (subtitulo != null)
                Text(
                  subtitulo!,
                  style: const TextStyle(
                    fontSize: 11,
                    color: COLOR_WHITE,
                  ),
                ),
            ],
          ),
        ),

        // 📂 Drawer
        drawer: Drawer(
          backgroundColor: COLOR_WHITE,
          child: Sidebar(isMobile: true),
        ),

        // 🧠 Conteúdo
        body: Column(
          children: [
            // 🔴 Barra OFFLINE
            if (!conectado)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                color: COLOR_WARNING,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.wifi_off, size: 14, color: Colors.black87),
                    SizedBox(width: 5),
                    Text(
                      'TRABALHANDO OFFLINE',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: Colors.black87,
                      ),
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
          // Sidebar fixa
          const Sidebar(),

          // Conteúdo
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
