'use client';

import { motion } from 'framer-motion';
import { CardProps, CardHeaderProps, CardBodyProps, CardFooterProps } from './Card.types';
import { cardStyles, cardHeaderStyles, cardBodyStyles, cardFooterStyles } from './Card.styles';
import { cn } from '../../../lib/utils';

export function Card({ 
  children, 
  className, 
  padding = 'md', 
  variant = 'default', 
  hoverable = false,
  onClick 
}: CardProps) {
  const Component = onClick ? motion.div : 'div';
  const props = onClick ? {
    whileHover: hoverable ? { scale: 1.01 } : {},
    whileTap: hoverable ? { scale: 0.99 } : {},
    onClick
  } : {};

  return (
    <Component
      className={cn(cardStyles({ variant, padding, hoverable }), className)}
      {...props}
    >
      {children}
    </Component>
  );
}

export function CardHeader({ children, className, actions }: CardHeaderProps) {
  return (
    <div className={cn(cardHeaderStyles, className)}>
      <div>{children}</div>
      {actions && <div>{actions}</div>}
    </div>
  );
}

export function CardBody({ children, className }: CardBodyProps) {
  return (
    <div className={cn(cardBodyStyles, className)}>
      {children}
    </div>
  );
}

export function CardFooter({ children, className }: CardFooterProps) {
  return (
    <div className={cn(cardFooterStyles, className)}>
      {children}
    </div>
  );
}