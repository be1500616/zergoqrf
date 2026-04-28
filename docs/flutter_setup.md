# Flutter Setup

This document outlines the steps to set up the Flutter development environment for the ZERGO QR project.

## 1. Install Flutter

Follow the official Flutter documentation to install the Flutter SDK on your operating system:
[https://flutter.dev/docs/get-started/install](https://flutter.dev/docs/get-started/install)

## 2. Configure your editor

Configure your editor with the Flutter and Dart plugins. For VS Code, install the following extensions:

- `Dart-Code.dart-code`
- `Dart-Code.flutter`

## 3. Verify your installation

Run the following command to check for any missing dependencies:

```bash
flutter doctor
```

Address any issues reported by `flutter doctor`.

## 4. Install project dependencies

Navigate to the frontend application directory and install the required packages:

```bash
cd apps/frontend
flutter pub get
```

## 5. Run the application

You can run the application using the VS Code launch configuration ("Flutter: Web") or by running the following command in the `apps/frontend` directory:

```bash
flutter run -d chrome --web-port 3000
```

The application will be available at `http://localhost:3000`. Hot reload is enabled by default.

## 6. Environment Configuration

The frontend is configured to connect to the local backend API. This is set up in the application code and does not require any manual configuration in a `.env` file for the frontend.
