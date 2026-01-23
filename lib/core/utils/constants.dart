import 'package:flutter/material.dart';

/// =======================================================
/// 🎨 IDENTIDADE VISUAL — VINHO & BRONZE
/// =======================================================

// Cores principais (Branding)
const COLOR_PRIMARY = Color(0xFF6A1B1B);     // Vinho escuro
const COLOR_SECONDARY = Color(0xFFB8860B);   // Bronze / dourado
const COLOR_TERTIARY = Color(0xFFF5DEB3);    // Bege suave
const COLOR_BACKGROUND = Color(0xFFFDFCFB);  // Off-white quente
const COLOR_WHITE = Color(0xFFFFFFFF);
const COLOR_TEXT = Color(0xFF2C1810);        // Marrom café

/// =======================================================
/// 🚦 CORES DE STATUS (Semânticas)
/// =======================================================

const COLOR_SUCCESS = Color(0xFF2E7D32); // Verde
const COLOR_WARNING = Color(0xFFF57C00); // Laranja
const COLOR_ERROR = Color(0xFFC62828);   // Vermelho
const COLOR_INFO = Color(0xFF1565C0);    // Azul

/// =======================================================
/// 🌫️ SOMBRAS
/// =======================================================

const SHADOW_SM = BoxShadow(
  blurRadius: 8,
  spreadRadius: 1,
  color: Color(0x0D000000), // 5% preto
  offset: Offset(0, 2),
);

const SHADOW_MD = BoxShadow(
  blurRadius: 20,
  spreadRadius: -5,
  color: Color(0x1A000000), // 10% preto
  offset: Offset(0, 8),
);

/// =======================================================
/// 🔲 BORDAS
/// =======================================================

const double BORDER_RADIUS_SM = 8;
const double BORDER_RADIUS_MD = 12;
const double BORDER_RADIUS_LG = 20;

/// =======================================================
/// 🔤 TIPOGRAFIA
/// =======================================================

const double FONT_SIZE_H1 = 28;
const double FONT_SIZE_H2 = 20;
const double FONT_SIZE_BODY = 14;

/// =======================================================
/// 🔐 AUTENTICAÇÃO / ROLES
/// ⚠️ Depois isso vira ENV / Firebase / SecureStorage
/// =======================================================

const String AUTH_EMAIL = 'marmoraria.central@gmail.com';
const String AUTH_PASSWORD = 'MarmorariaC55';

const String ROLE_ADMIN = 'admin';
const String ROLE_PRODUCAO = 'producao';

/// =======================================================
/// 📐 LAYOUT
/// =======================================================

const double PADDING_VIEW = 30;
