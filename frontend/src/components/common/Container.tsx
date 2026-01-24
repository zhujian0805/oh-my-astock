import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
  fluid?: boolean;
}

const Container: React.FC<ContainerProps> = ({ children, className = '', fluid = false }) => {
  return (
    <div className={`mx-auto px-4 sm:px-6 lg:px-8 ${fluid ? 'w-full' : 'max-w-7xl'} ${className}`}>
      {children}
    </div>
  );
};

export default Container;
