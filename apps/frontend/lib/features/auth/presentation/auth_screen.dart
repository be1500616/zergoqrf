import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:get/get.dart';

import '../../../core/theme/app_animations.dart';
import '../../../core/theme/app_spacing.dart';
import '../../../core/theme/widgets/theme_toggle_button.dart';
import '../../../shared/responsive/index.dart';
import '../../../shared/utils/india_phone_input_formatter.dart';
import '../../../shared/utils/validation_utils.dart';
import '../application/supabase_auth_controller.dart';
import 'widgets/food_background_visual.dart';

/// Enhanced authentication screen with modern, food-themed design
///
/// Features:
/// - Responsive two-column layout (desktop/tablet) and stacked layout (mobile)
/// - Food-themed visual branding column
/// - Social login integration (Google, Apple)
/// - Three authentication methods: Staff (email/password), Customer (phone OTP), Restaurant Code
/// - Smooth animations and transitions
/// - Dark mode support
class AuthScreen extends GetView<SupabaseAuthController> {
  const AuthScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final screenSize = ScreenSize.of(context);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      body: SafeArea(
        child: ResponsiveLayout(
          mobile: _buildMobileLayout(context, theme, screenSize),
          tablet: _buildTabletDesktopLayout(context, theme, screenSize),
          desktop: _buildTabletDesktopLayout(context, theme, screenSize),
        ),
      ),
    );
  }

  /// Mobile layout - Stacked visual on top, form below
  Widget _buildMobileLayout(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Visual branding section at top (mobile)
          SizedBox(
            height: 250,
            child: FoodBackgroundVisual(
              isCompact: true,
              onDismiss: () {}, // No dismiss on mobile
            ),
          )
              .animate()
              .fadeIn(duration: AppAnimations.normal)
              .slideY(begin: -0.2, end: 0),

          // Theme toggle button positioned over visual
          const Padding(
            padding: EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                ThemeToggleIconButton(),
              ],
            ),
          ),

          // Form section
          Padding(
            padding:
                EdgeInsets.all(AppSpacing.lg * screenSize.spacingMultiplier),
            child: Column(
              children: [
                _buildAuthTabs(context, theme, screenSize),
                SizedBox(
                    height:
                        AppSpacing.micro * screenSize.spacingMultiplier * 0.5),
                _buildAnonymousAccess(context, theme, screenSize),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Tablet and Desktop layout - Two-column side-by-side
  Widget _buildTabletDesktopLayout(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return Row(
      children: [
        // Left Column: Food-themed visual branding
        Expanded(
          flex: screenSize.isTablet ? 4 : 5,
          child: const FoodBackgroundVisual(
            isCompact: false,
            onDismiss: null, // No dismiss on desktop
          )
              .animate()
              .fadeIn(duration: AppAnimations.slow)
              .slideX(begin: -0.3, end: 0),
        ),

        // Right Column: Authentication forms
        Expanded(
          flex: screenSize.isTablet ? 6 : 5,
          child: Container(
            color: theme.colorScheme.surface,
            child: SingleChildScrollView(
              padding: EdgeInsets.all(
                screenSize.responsiveValue(
                  mobile: AppSpacing.xl,
                  tablet: AppSpacing.xxl,
                  desktop: AppSpacing.xxl * 1.5,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Theme toggle at top right
                  const Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      ThemeToggleIconButton(),
                    ],
                  ),
                  SizedBox(
                      height:
                          AppSpacing.xl * (screenSize.spacingMultiplier * 0.3)),

                  // Logo
                  _buildLogoHeader(theme, screenSize)
                      .animate(delay: 200.ms)
                      .fadeIn(duration: AppAnimations.normal)
                      .slideY(begin: -0.2, end: 0),

                  SizedBox(
                      height: AppSpacing.xxl *
                          (screenSize.spacingMultiplier * 0.5)),

                  // Auth tabs
                  _buildAuthTabs(context, theme, screenSize)
                      .animate(delay: 400.ms)
                      .fadeIn(duration: AppAnimations.normal)
                      .slideY(begin: 0.2, end: 0),

                  // SizedBox(
                  //     height: AppSpacing.md * screenSize.spacingMultiplier),

                  // Anonymous access section
                  _buildAnonymousAccess(context, theme, screenSize)
                      .animate(delay: 600.ms)
                      .fadeIn(duration: AppAnimations.normal),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  /// Logo header for desktop/tablet layout
  Widget _buildLogoHeader(ThemeData theme, ScreenSize screenSize) {
    return Column(
      children: [
        // Logo
        Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                theme.primaryColor,
                theme.colorScheme.secondary,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: theme.primaryColor.withOpacity(0.3),
                blurRadius: 15,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Icon(
            Icons.restaurant_menu,
            size: 40,
            color: theme.colorScheme.onPrimary,
          ),
        ),
        const SizedBox(height: AppSpacing.md),
        Text(
          'ZERGO QR',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onSurface,
          ),
        ),
      ],
    );
  }

  /// Auth tabs container with Staff and Customer options
  Widget _buildAuthTabs(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return Container(
      decoration: BoxDecoration(
        color: theme.colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: theme.colorScheme.outline.withOpacity(0.1),
        ),
      ),
      child: DefaultTabController(
        length: 2,
        child: Column(
          children: [
            // Custom tab bar
            Container(
              decoration: BoxDecoration(
                color:
                    theme.colorScheme.surfaceContainerHighest.withOpacity(0.3),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                ),
              ),
              child: TabBar(
                labelColor: theme.colorScheme.primary,
                unselectedLabelColor: theme.colorScheme.onSurfaceVariant,
                indicatorColor: theme.colorScheme.primary,
                indicatorWeight: 3,
                indicatorSize: TabBarIndicatorSize.tab,
                dividerColor: Colors.transparent, // Remove default divider
                labelStyle: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                unselectedLabelStyle: theme.textTheme.titleMedium,
                tabs: const [
                  Tab(
                    text: 'Customer',
                    icon: Icon(Icons.person_outline, size: 20),
                  ),
                  Tab(
                    text: 'Staff Login',
                    icon: Icon(Icons.badge_outlined, size: 20),
                  ),
                ],
              ),
            ),

            // Tab content
            SizedBox(
              height: screenSize.responsiveValue(
                mobile: 300.0,
                tablet: 400.0,
                desktop: 400.0,
              ),
              child: TabBarView(
                children: [
                  _buildCustomerTab(context, theme, screenSize),
                  _buildStaffLoginTab(context, theme, screenSize),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Staff login tab with email/password and social login
  Widget _buildStaffLoginTab(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return SingleChildScrollView(
      padding: EdgeInsets.all(AppSpacing.lg * screenSize.spacingMultiplier),
      child: Form(
        key: controller.staffLoginFormKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Text(
              'Welcome Back!',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.onSurface,
              ),
              textAlign: TextAlign.center,
            )
                .animate(delay: 100.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideY(begin: -0.2, end: 0),

            SizedBox(height: AppSpacing.sm * screenSize.spacingMultiplier),

            Text(
              'Sign in to manage your restaurant',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ).animate(delay: 200.ms).fadeIn(duration: AppAnimations.normal),

            SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

            // Email field with enhanced styling
            TextFormField(
              controller: controller.emailController,
              decoration: InputDecoration(
                labelText: 'Email',
                hintText: 'Enter your email address',
                prefixIcon: Icon(
                  Icons.email_outlined,
                  color: theme.primaryColor,
                  size: 22,
                ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: theme.colorScheme.outline.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(
                    color: theme.colorScheme.outline.withOpacity(0.5),
                    width: 1.5,
                  ),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide(color: theme.primaryColor, width: 2.5),
                ),
                filled: true,
                fillColor: theme.colorScheme.surface,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 18,
                ),
              ),
              style: theme.textTheme.bodyLarge,
              keyboardType: TextInputType.emailAddress,
              textInputAction: TextInputAction.next,
              validator: EmailValidator.validate,
            )
                .animate(delay: 300.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideX(begin: -0.2, end: 0),

            SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),

            // Password field with enhanced styling
            Obx(() => TextFormField(
                      controller: controller.passwordController,
                      decoration: InputDecoration(
                        labelText: 'Password',
                        hintText: 'Enter your password',
                        prefixIcon: Icon(
                          Icons.lock_outline,
                          color: theme.primaryColor,
                          size: 22,
                        ),
                        suffixIcon: IconButton(
                          icon: Icon(
                            controller.isPasswordVisible.value
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                          onPressed: controller.togglePasswordVisibility,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: theme.colorScheme.outline.withOpacity(0.5),
                            width: 1.5,
                          ),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(
                            color: theme.colorScheme.outline.withOpacity(0.5),
                            width: 1.5,
                          ),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide:
                              BorderSide(color: theme.primaryColor, width: 2.5),
                        ),
                        filled: true,
                        fillColor: theme.colorScheme.surface,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 18,
                        ),
                      ),
                      style: theme.textTheme.bodyLarge,
                      obscureText: !controller.isPasswordVisible.value,
                      textInputAction: TextInputAction.done,
                      validator: (value) => PasswordValidator.validate(value),
                      onFieldSubmitted: (_) {
                        if (controller.staffLoginFormKey.currentState
                                ?.validate() ??
                            false) {
                          if (controller.canSignIn.value &&
                              !controller.isLoading.value) {
                            controller.signInWithEmail();
                          }
                        }
                      },
                    ))
                .animate(delay: 400.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideX(begin: -0.2, end: 0),

            SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

            // Enhanced sign in button
            Obx(() => SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: controller.canSignIn.value &&
                                !controller.isLoading.value
                            ? () {
                                if (controller.staffLoginFormKey.currentState
                                        ?.validate() ??
                                    false) {
                                  controller.signInWithEmail();
                                }
                              }
                            : null,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.primaryColor,
                          foregroundColor: theme.colorScheme.onPrimary,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 2,
                          shadowColor: theme.primaryColor.withOpacity(0.3),
                        ),
                        child: controller.isLoading.value
                            ? SizedBox(
                                height: 24,
                                width: 24,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2.5,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    theme.colorScheme.onPrimary,
                                  ),
                                ),
                              )
                            : Text(
                                'Sign In',
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: theme.colorScheme.onPrimary,
                                ),
                              ),
                      ),
                    ))
                .animate(delay: 500.ms)
                .fadeIn(duration: AppAnimations.normal)
                .slideY(begin: 0.2, end: 0)
                .shimmer(
                  delay: 1000.ms,
                  duration: 2000.ms,
                  color: theme.colorScheme.onPrimary.withOpacity(0.3),
                ),

            SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),

            // Footer links
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'New staff member?',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                TextButton(
                  onPressed: () => _showStaffRegistration(context),
                  child: Text(
                    'Register here',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.primaryColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ).animate(delay: 600.ms).fadeIn(duration: AppAnimations.normal),
          ],
        ),
      ),
    );
  }

  Widget _buildCustomerTab(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return SingleChildScrollView(
      padding: EdgeInsets.all(AppSpacing.lg * screenSize.spacingMultiplier),
      child: Obx(() {
        if (controller.isOtpSent.value) {
          return _buildOtpVerificationForm(context, theme, screenSize);
        } else {
          return _buildPhoneLoginForm(context, theme, screenSize);
        }
      }),
    );
  }

  Widget _buildPhoneLoginForm(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return Form(
      key: controller.customerFormKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Text(
            'Welcome!',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onSurface,
            ),
            textAlign: TextAlign.center,
          )
              .animate(delay: 100.ms)
              .fadeIn(duration: AppAnimations.normal)
              .slideY(begin: -0.2, end: 0),

          SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),

          Text(
            'Enter your phone number to get started',
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            textAlign: TextAlign.center,
          ).animate(delay: 200.ms).fadeIn(duration: AppAnimations.normal),

          SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

          // Phone number input with India country code
          TextFormField(
            controller: controller.phoneController,
            decoration: InputDecoration(
              labelText: 'Phone Number',
              hintText: '+91 9876543210',
              helperText: 'India phone number with country code',
              prefixIcon: Icon(
                Icons.phone_rounded,
                color: theme.primaryColor,
                size: 22,
              ),
              filled: true,
              fillColor: theme.colorScheme.surface,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.5),
                  width: 1.5,
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.5),
                  width: 1.5,
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.primaryColor,
                  width: 2.5,
                ),
              ),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: 16,
                vertical: 18,
              ),
            ),
            style: theme.textTheme.bodyLarge,
            keyboardType: TextInputType.phone,
            inputFormatters: [IndiaPhoneInputFormatter()],
            validator: PhoneValidator.validate,
          )
              .animate()
              .fadeIn(delay: 300.ms, duration: 400.ms)
              .slideY(begin: 0.2, end: 0, curve: Curves.easeOut),

          SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),

          // Helper text
          Text(
            'We\'ll send you a verification code to confirm your phone number.',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurface.withOpacity(0.6),
            ),
            textAlign: TextAlign.center,
          ).animate().fadeIn(delay: 400.ms, duration: 400.ms),

          SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

          // Send OTP button
          Obx(
            () => SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed:
                    controller.canSendOtp.value && !controller.isLoading.value
                        ? () {
                            if (controller.customerFormKey.currentState
                                    ?.validate() ??
                                false) {
                              controller.signInWithPhone();
                            }
                          }
                        : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.primaryColor,
                  foregroundColor: theme.colorScheme.onPrimary,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: controller.isLoading.value
                    ? SizedBox(
                        height: 24,
                        width: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: theme.colorScheme.onPrimary,
                        ),
                      )
                    : Text(
                        'Send Verification Code',
                        style: theme.textTheme.titleMedium?.copyWith(
                          color: theme.colorScheme.onPrimary,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
              ),
            ),
          )
              .animate()
              .fadeIn(delay: 500.ms, duration: 400.ms)
              .slideY(begin: 0.2, end: 0, curve: Curves.easeOut)
              .shimmer(
                delay: 1500.ms,
                duration: AppAnimations.extraSlow,
                color: theme.colorScheme.onPrimary.withOpacity(0.3),
              ),
        ],
      ),
    );
  }

  Widget _buildOtpVerificationForm(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return Form(
      key: controller.otpVerificationFormKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: theme.primaryColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: theme.primaryColor.withOpacity(0.3),
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.message_rounded,
                  color: theme.primaryColor,
                  size: 24,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Enter the 6-digit code sent to\n${controller.phoneController.text}',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurface,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          )
              .animate()
              .fadeIn(duration: 400.ms)
              .slideY(begin: -0.2, end: 0, curve: Curves.easeOut),

          const SizedBox(height: 24),

          // Name field (optional)
          TextFormField(
            controller: controller.nameController,
            decoration: InputDecoration(
              labelText: 'Your Name (Optional)',
              hintText: 'John Doe',
              prefixIcon: Icon(
                Icons.person_rounded,
                color: theme.primaryColor,
              ),
              filled: true,
              fillColor: theme.colorScheme.surface,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.3),
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.3),
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.primaryColor,
                  width: 2,
                ),
              ),
            ),
            validator: (value) =>
                NameValidator.validate(value, required: false),
          )
              .animate()
              .fadeIn(delay: 200.ms, duration: 400.ms)
              .slideY(begin: 0.2, end: 0, curve: Curves.easeOut),

          const SizedBox(height: 16),

          // OTP input
          TextFormField(
            controller: controller.otpController,
            decoration: InputDecoration(
              labelText: 'Verification Code',
              hintText: '000000',
              prefixIcon: Icon(
                Icons.verified_user_rounded,
                color: theme.primaryColor,
              ),
              filled: true,
              fillColor: theme.colorScheme.surface,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.3),
                ),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.3),
                ),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide(
                  color: theme.primaryColor,
                  width: 2,
                ),
              ),
              counterText: '',
            ),
            keyboardType: TextInputType.number,
            maxLength: 6,
            textAlign: TextAlign.center,
            style: theme.textTheme.headlineSmall?.copyWith(
              letterSpacing: 8,
              fontWeight: FontWeight.bold,
            ),
            validator: OTPValidator.validate,
          )
              .animate()
              .fadeIn(delay: 300.ms, duration: 400.ms)
              .slideY(begin: 0.2, end: 0, curve: Curves.easeOut),

          const SizedBox(height: 24),

          // Verify button
          Obx(
            () => SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed:
                    controller.canVerifyOtp.value && !controller.isLoading.value
                        ? () {
                            if (controller.otpVerificationFormKey.currentState
                                    ?.validate() ??
                                false) {
                              controller.verifyOtp();
                            }
                          }
                        : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.primaryColor,
                  foregroundColor: theme.colorScheme.onPrimary,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: controller.isLoading.value
                    ? SizedBox(
                        height: 24,
                        width: 24,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: theme.colorScheme.onPrimary,
                        ),
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.check_circle_rounded),
                          const SizedBox(width: 8),
                          Text(
                            'Verify & Continue',
                            style: theme.textTheme.titleMedium?.copyWith(
                              color: theme.colorScheme.onPrimary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
          )
              .animate()
              .fadeIn(delay: 400.ms, duration: 400.ms)
              .slideY(begin: 0.2, end: 0, curve: Curves.easeOut)
              .shimmer(
                delay: 1500.ms,
                duration: AppAnimations.extraSlow,
                color: theme.colorScheme.onPrimary.withOpacity(0.3),
              ),

          const SizedBox(height: 24),

          // Action buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton.icon(
                onPressed: () {
                  controller.isOtpSent.value = false;
                  controller.otpController.clear();
                },
                icon: const Icon(Icons.arrow_back_rounded),
                label: const Text('Change Number'),
                style: TextButton.styleFrom(
                  foregroundColor: theme.colorScheme.primary,
                ),
              ),
              TextButton.icon(
                onPressed: controller.isLoading.value
                    ? null
                    : controller.signInWithPhone,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('Resend Code'),
                style: TextButton.styleFrom(
                  foregroundColor: theme.colorScheme.primary,
                ),
              ),
            ],
          ).animate().fadeIn(delay: 500.ms, duration: 400.ms),
        ],
      ),
    );
  }

  Widget _buildAnonymousAccess(
      BuildContext context, ThemeData theme, ScreenSize screenSize) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // OR divider
        Row(
          children: [
            Expanded(
              child: Divider(
                thickness: 1.5,
                color: theme.colorScheme.outlineVariant,
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                'OR',
                style: theme.textTheme.labelLarge?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 1.2,
                ),
              ),
            ),
            Expanded(
              child: Divider(
                thickness: 1.5,
                color: theme.colorScheme.outlineVariant,
              ),
            ),
          ],
        ).animate(delay: 100.ms).fadeIn(
              duration: AppAnimations.normal,
              curve: AppAnimations.decelerate,
            ),

        SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

        // Restaurant Code Form
        Form(
          key: controller.restaurantCodeFormKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Restaurant Code input
              TextFormField(
                controller: controller.restaurantCodeController,
                decoration: InputDecoration(
                  labelText: 'Restaurant Code',
                  hintText: 'Enter 6-character code',
                  prefixIcon: Icon(
                    Icons.restaurant,
                    color: theme.colorScheme.primary,
                  ),
                  filled: true,
                  fillColor: theme.colorScheme.surface,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(
                      color: theme.colorScheme.outline,
                    ),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(
                      color: theme.colorScheme.primary,
                      width: 2,
                    ),
                  ),
                  errorBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(
                      color: theme.colorScheme.error,
                    ),
                  ),
                  focusedErrorBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(
                      color: theme.colorScheme.error,
                      width: 2,
                    ),
                  ),
                ),
                textCapitalization: TextCapitalization.characters,
                style: theme.textTheme.bodyLarge?.copyWith(
                  fontWeight: FontWeight.w500,
                  letterSpacing: 2,
                ),
                validator: RestaurantCodeValidator.validate,
                onChanged: (value) {
                  // Format as uppercase
                  final formatted = RestaurantCodeValidator.format(value);
                  if (formatted != value) {
                    controller.restaurantCodeController.value =
                        TextEditingValue(
                      text: formatted,
                      selection: TextSelection.collapsed(
                        offset: formatted.length,
                      ),
                    );
                  }
                },
              )
                  .animate(delay: 200.ms)
                  .fadeIn(
                    duration: AppAnimations.normal,
                    curve: AppAnimations.decelerate,
                  )
                  .slideY(
                    begin: 0.2,
                    end: 0,
                    duration: AppAnimations.normal,
                    curve: AppAnimations.decelerate,
                  ),

              SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),

              // Helper text
              Text(
                'Ask your server for the restaurant code',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ).animate(delay: 300.ms).fadeIn(
                    duration: AppAnimations.normal,
                    curve: AppAnimations.decelerate,
                  ),

              SizedBox(height: AppSpacing.md * screenSize.spacingMultiplier),

              // Submit button
              Obx(
                () => SizedBox(
                  height: 56,
                  child: ElevatedButton.icon(
                    onPressed: controller.isLoading.value
                        ? null
                        : () {
                            if (controller.restaurantCodeFormKey.currentState
                                    ?.validate() ??
                                false) {
                              controller.validateRestaurantCode();
                            }
                          },
                    icon: controller.isLoading.value
                        ? const SizedBox.shrink()
                        : const Icon(Icons.login),
                    label: controller.isLoading.value
                        ? SizedBox(
                            height: 24,
                            width: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2.5,
                              color: theme.colorScheme.onPrimary,
                            ),
                          )
                        : const Text('Access Restaurant'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: theme.colorScheme.primary,
                      foregroundColor: theme.colorScheme.onPrimary,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 2,
                    ),
                  ),
                ),
              )
                  .animate(delay: 400.ms)
                  .fadeIn(
                    duration: AppAnimations.normal,
                    curve: AppAnimations.decelerate,
                  )
                  .slideY(
                    begin: 0.2,
                    end: 0,
                    duration: AppAnimations.normal,
                    curve: AppAnimations.decelerate,
                  )
                  .shimmer(
                    delay: 1200.ms,
                    duration: AppAnimations.extraSlow,
                    color: theme.colorScheme.onPrimary.withOpacity(0.3),
                  ),
            ],
          ),
        ),

        SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

        // Divider
        Divider(
          thickness: 1,
          color: theme.colorScheme.outlineVariant,
        ).animate(delay: 500.ms).fadeIn(
              duration: AppAnimations.normal,
              curve: AppAnimations.decelerate,
            ),

        SizedBox(height: AppSpacing.lg * screenSize.spacingMultiplier),

        // QR Scanner button
        SizedBox(
          height: 56,
          child: OutlinedButton.icon(
            onPressed: () => _showQRScanner(context),
            icon: Icon(
              Icons.qr_code_scanner,
              color: theme.colorScheme.primary,
              size: 24,
            ),
            label: Text(
              'Scan QR Code',
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w600,
              ),
            ),
            style: OutlinedButton.styleFrom(
              side: BorderSide(
                color: theme.colorScheme.primary,
                width: 2,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        )
            .animate(delay: 600.ms)
            .fadeIn(
              duration: AppAnimations.normal,
              curve: AppAnimations.decelerate,
            )
            .slideY(
              begin: 0.2,
              end: 0,
              duration: AppAnimations.normal,
              curve: AppAnimations.decelerate,
            ),

        SizedBox(height: AppSpacing.xs * screenSize.spacingMultiplier),

        // QR Scanner helper text
        Text(
          'Scan the QR code at your table for instant access',
          textAlign: TextAlign.center,
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ).animate(delay: 700.ms).fadeIn(
              duration: AppAnimations.normal,
              curve: AppAnimations.decelerate,
            ),
      ],
    );
  }

  void _showStaffRegistration(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Staff Registration'),
        content: const Text(
          'Staff registration requires an invitation from your restaurant manager. '
          'Please contact your manager to get access credentials.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  void _showQRScanner(BuildContext context) {
    // This would typically open a QR scanner
    // For now, we'll show a dialog
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('QR Code Scanner'),
        content: const Text(
          'Scan the QR code on your table to access the menu and place orders anonymously.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              // Demo: Create anonymous session
              controller.createAnonymousSession(
                restaurantId: 'demo-restaurant-id',
                tableId: 'demo-table-id',
              );
            },
            child: const Text('Demo Access'),
          ),
        ],
      ),
    );
  }
}
