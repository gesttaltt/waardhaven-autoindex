'use client';

import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { ButtonProps } from './Button.types';
import { buttonStyles, loadingSpinnerStyles } from './Button.styles';

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      fullWidth = false,
      disabled = false,
      loading = false,
      type = 'button',
      onClick,
      children,
      className,
      'aria-label': ariaLabel,
      ...props
    },
    ref
  ) => {
    const isDisabled = disabled || loading;

    return (
      <motion.button
        ref={ref}
        type={type}
        disabled={isDisabled}
        onClick={onClick}
        className={buttonStyles({ variant, size, fullWidth, className })}
        aria-label={ariaLabel}
        whileHover={!isDisabled ? { scale: 1.02 } : {}}
        whileTap={!isDisabled ? { scale: 0.98 } : {}}
        {...props}
      >
        {loading && (
          <span className={loadingSpinnerStyles} aria-hidden="true" />
        )}
        {children}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';