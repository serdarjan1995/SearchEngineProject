import React from 'react';
import { Box, Typography } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

function Processing({ message }) {
    return (
        <Box sx={styles.container}>
            <Box sx={styles.iconWrapper}>
                <SearchIcon sx={styles.icon} />
            </Box>
            <Typography variant="h6" sx={styles.message}>
                {message || 'Processing your search...'}
            </Typography>
        </Box>
    );
}

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '300px',
        textAlign: 'center',
    },
    iconWrapper: {
        animation: 'bouncePulse 2s infinite ease-in-out',
        '@keyframes bouncePulse': {
            '0%, 100%': {
                transform: 'translateY(0px) scale(1) rotate(0deg)',
            },
            '30%': {
                transform: 'translateY(-10px) scale(1.1) rotate(-5deg)',
            },
            '60%': {
                transform: 'translateY(5px) scale(0.95) rotate(5deg)',
            },
        },
    },
    icon: {
        fontSize: 80,
        color: '#1a73e8',
    },
    message: {
        marginTop: '20px',
        color: '#5f6368',
    },
};

export default Processing;