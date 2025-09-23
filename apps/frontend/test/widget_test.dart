// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:zergo_frontend/main.dart';

void main() {
  testWidgets('ZergoApp renders home screen', (tester) async {
    await tester.pumpWidget(const ZergoApp());

    // Basic smoke: app title text should appear somewhere
    expect(find.text('ZERGO QR'), findsWidgets);
  });
}
