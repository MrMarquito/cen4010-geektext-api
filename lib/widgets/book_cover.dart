import 'package:flutter/material.dart';

class BookCover extends StatelessWidget {
  final String title;
  final String genre;
  final String publisher;
  final double width;
  final double height;

  const BookCover({
    super.key,
    required this.title,
    required this.genre,
    required this.publisher,
    this.width = 140,
    this.height = 200,
  });

  List<Color> _getGenreGradient(String g) {
    switch (g.toLowerCase()) {
      case 'technology':
        return [const Color(0xFF0F766E), const Color(0xFF042F2E)];
      case 'sci-fi':
        return [const Color(0xFF1E40AF), const Color(0xFF0F172A)];
      case 'fantasy':
        return [const Color(0xFF6B21A8), const Color(0xFF3B0764)];
      case 'fiction':
        return [const Color(0xFF9F1239), const Color(0xFF4C0519)];
      default:
        return [const Color(0xFF334155), const Color(0xFF0F172A)];
    }
  }

  @override
  Widget build(BuildContext context) {
    final gradient = _getGenreGradient(genre);

    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        borderRadius: const BorderRadius.only(
          topRight: Radius.circular(8),
          bottomRight: Radius.circular(8),
          topLeft: Radius.circular(3),
          bottomLeft: Radius.circular(3),
        ),
        gradient: LinearGradient(
          colors: gradient,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 10,
            offset: const Offset(4, 6),
          ),
        ],
      ),
      child: Stack(
        children: [
          // Book spine depth illusion
          Positioned(
            left: 0,
            top: 0,
            bottom: 0,
            child: Container(
              width: 9,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.black.withOpacity(0.4),
                    Colors.white.withOpacity(0.15),
                    Colors.black.withOpacity(0.2),
                  ],
                ),
              ),
            ),
          ),
          // Cover typography & framing
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 12, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade400.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: Colors.amber.shade300.withOpacity(0.5)),
                  ),
                  child: Text(
                    genre.toUpperCase(),
                    style: TextStyle(
                      color: Colors.amber.shade200,
                      fontSize: 9,
                      fontWeight: FontWeight.w800,
                      letterSpacing: 1.0,
                    ),
                  ),
                ),
                const Spacer(),
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 13,
                    height: 1.2,
                  ),
                  maxLines: 4,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                Text(
                  publisher,
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.65),
                    fontSize: 10,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
