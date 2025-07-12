# Byte Board Blog CSS Architecture

This document outlines the CSS architecture for the Byte Board Blog project.

## CSS Files Organization

The CSS for this project is organized into several files, each with a specific purpose:

1. **theme.css**: Contains CSS variables and theme configuration
2. **utilities.css**: Provides utility classes for common styling needs
3. **main.css**: Contains global styles and base element styling
4. **components.css**: Contains styles specific to individual components
5. **responsive.css**: Contains media queries and responsive design rules

## Loading Order

The CSS files are loaded in the following order:

1. Bootstrap CSS (from CDN)
2. Google Fonts (from CDN)
3. theme.css
4. utilities.css
5. main.css
6. components.css
7. responsive.css

This order ensures that our custom styles can override Bootstrap styles when needed, and that the theme variables and utility classes are available to all our custom CSS files.

## Theme Variables

The `theme.css` file contains CSS variables that define the theme of the application. These variables are used throughout the other CSS files to ensure consistent styling. Some of the key variables include:

- Color variables (primary, secondary, accent, etc.)
- Typography variables (font families, sizes, weights)
- Spacing variables
- Border radius and shadow variables
- Transition variables

## Utility Classes

The `utilities.css` file provides a set of utility classes that can be used to apply common styles without writing custom CSS. These include:

- Spacing utilities (margin, padding)
- Typography utilities (font size, weight, alignment)
- Display utilities
- Flex utilities
- Border utilities
- Shadow utilities
- Position utilities
- Visibility utilities

## Responsive Design

The responsive design is implemented using:

1. Bootstrap's responsive grid system
2. Custom media queries in the `responsive.css` file
3. Responsive utility classes

The application is designed to work well on all screen sizes, from mobile phones to large desktop monitors.

## Adding New Styles

When adding new styles to the application:

1. Use existing theme variables from `theme.css` whenever possible
2. Use utility classes from `utilities.css` for common styling needs
3. Add component-specific styles to `components.css`
4. Add responsive adjustments to `responsive.css`
5. Only add global styles to `main.css` if they apply to the entire application

## Best Practices

1. Follow the BEM (Block, Element, Modifier) naming convention for CSS classes
2. Use CSS variables for consistent styling
3. Keep selectors as simple as possible
4. Avoid using !important unless absolutely necessary (utility classes are an exception)
5. Test styles on multiple screen sizes