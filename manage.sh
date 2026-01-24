#!/bin/bash

# oh-my-astock Management Script
# Manages frontend (React/Vite) and backend (Python/FastAPI) services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/backend"
FRONTEND_DIR="${SCRIPT_DIR}/frontend"

# PID files
BACKEND_PID_FILE="/tmp/oh-my-astock-backend.pid"
FRONTEND_PID_FILE="/tmp/oh-my-astock-frontend.pid"

# Log files
LOG_DIR="${SCRIPT_DIR}/logs"
BACKEND_LOG="${LOG_DIR}/backend.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Check if a service is running
is_running() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$pid_file"
            return 1
        fi
    fi
    return 1
}

# Check dependencies
check_dependencies() {
    print_header "Checking Dependencies"

    local missing_deps=0

    # Check Python
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version)
        print_success "Python: ${python_version}"
    else
        print_error "Python3 not found. Please install Python >= 3.10"
        missing_deps=1
    fi

    # Check pip
    if command -v pip3 &> /dev/null; then
        local pip_version=$(pip3 --version | awk '{print $2}')
        print_success "pip: v${pip_version}"
    else
        print_error "pip3 not found. Please install pip >= 21.0"
        missing_deps=1
    fi

    if [ $missing_deps -eq 1 ]; then
        print_error "Missing required dependencies. Please install them and try again."
        exit 1
    fi
}

# Install dependencies
install_deps() {
    print_header "Installing Dependencies"

    # Backend dependencies (Python)
    print_info "Installing backend Python dependencies..."
    cd "$BACKEND_DIR"
    pip3 install -r requirements.txt
    print_success "Backend Python dependencies installed"

    # Frontend dependencies
    if [ -d "$FRONTEND_DIR" ]; then
        print_info "Installing frontend dependencies..."
        cd "$FRONTEND_DIR"
        npm install
        print_success "Frontend dependencies installed"
    else
        print_warning "Frontend directory not found at: $FRONTEND_DIR"
    fi

    cd "$SCRIPT_DIR"
}

# Setup environment files
setup_env() {
    print_header "Setting Up Environment Files"

    # Backend .env
    if [ -d "$BACKEND_DIR" ]; then
        if [ ! -f "$BACKEND_DIR/.env" ] && [ -f "$BACKEND_DIR/.env.example" ]; then
            print_info "Creating backend .env file..."
            cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
            print_success "Backend .env created from .env.example"
        else
            print_info "Backend .env already exists"
        fi
    fi

    # Frontend .env
    if [ -d "$FRONTEND_DIR" ]; then
        if [ ! -f "$FRONTEND_DIR/.env" ] && [ -f "$FRONTEND_DIR/.env.example" ]; then
            print_info "Creating frontend .env file..."
            cp "$FRONTEND_DIR/.env.example" "$FRONTEND_DIR/.env"
            print_success "Frontend .env created from .env.example"
        else
            print_info "Frontend .env already exists"
        fi
    fi
}

# Start backend
start_backend() {
    if is_running "$BACKEND_PID_FILE"; then
        print_warning "Backend is already running (PID: $(cat $BACKEND_PID_FILE))"
        return
    fi

    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Backend directory not found at: $BACKEND_DIR"
        return 1
    fi

    print_info "Starting backend server..."
    cd "$BACKEND_DIR"

    # Check if Python dependencies are installed
    if ! python3 -c "import fastapi, uvicorn, duckdb, pydantic" 2>/dev/null; then
        print_warning "Backend Python dependencies not installed. Installing now..."
        pip3 install -r requirements.txt
    fi

    # Start backend with uvicorn
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > "$BACKEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$BACKEND_PID_FILE"

    # Wait a moment and check if it's still running
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        print_success "Backend started (PID: $pid)"
        print_info "Backend logs: $BACKEND_LOG"
        print_info "Backend URL: http://localhost:8000"
    else
        print_error "Backend failed to start. Check logs at: $BACKEND_LOG"
        rm -f "$BACKEND_PID_FILE"
        return 1
    fi

    cd "$SCRIPT_DIR"
}

# Build frontend
build_frontend() {
    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found at: $FRONTEND_DIR"
        return 1
    fi

    print_info "Building frontend..."
    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Frontend dependencies not installed. Installing now..."
        npm install
    fi

    # Build the frontend
    if npm run build; then
        print_success "Frontend built successfully"
    else
        print_error "Frontend build failed"
        cd "$SCRIPT_DIR"
        return 1
    fi

    cd "$SCRIPT_DIR"
}

# Start frontend
start_frontend() {
    if is_running "$FRONTEND_PID_FILE"; then
        print_warning "Frontend is already running (PID: $(cat $FRONTEND_PID_FILE))"
        return
    fi

    if [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Frontend directory not found at: $FRONTEND_DIR"
        return 1
    fi

    print_info "Starting frontend server..."
    cd "$FRONTEND_DIR"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Frontend dependencies not installed. Installing now..."
        npm install
    fi

    # Start frontend in background
    npm run dev > "$FRONTEND_LOG" 2>&1 &
    local pid=$!
    echo $pid > "$FRONTEND_PID_FILE"

    # Wait a moment and check if it's still running
    sleep 2
    if kill -0 $pid 2>/dev/null; then
        print_success "Frontend started (PID: $pid)"
        print_info "Frontend logs: $FRONTEND_LOG"
        print_info "Frontend URL: http://localhost:4142"
    else
        print_error "Frontend failed to start. Check logs at: $FRONTEND_LOG"
        rm -f "$FRONTEND_PID_FILE"
        return 1
    fi

    cd "$SCRIPT_DIR"
}

# Stop backend
stop_backend() {
    print_info "Stopping backend..."
    local stopped=0
    
    # Method 1: Kill via PID file
    if [ -f "$BACKEND_PID_FILE" ]; then
        local pid=$(cat "$BACKEND_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_info "Killing backend process from PID file (PID: $pid)..."
            kill $pid 2>/dev/null || true
            stopped=1
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    # Method 2: Kill via Port 8000
    local port_pid=$(lsof -t -i:8000 -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$port_pid" ]; then
        # Check if it's multiple PIDs and iterate
        for p in $port_pid; do
            print_info "Killing backend process on port 8000 (PID: $p)..."
            kill -9 $p 2>/dev/null || true
            stopped=1
        done
    fi
    
    if [ $stopped -eq 1 ]; then
        # Wait for port to be free
        local retries=0
        while lsof -i:8000 -sTCP:LISTEN >/dev/null 2>&1; do
            sleep 0.5
            retries=$((retries+1))
            if [ $retries -gt 10 ]; then
                print_warning "Backend port 8000 still in use after waiting. Forcing kill..."
                 local stubborn_pid=$(lsof -t -i:8000 -sTCP:LISTEN 2>/dev/null || true)
                 if [ -n "$stubborn_pid" ]; then
                     kill -9 $stubborn_pid 2>/dev/null || true
                 fi
            fi
        done
        print_success "Backend stopped"
    else
        print_warning "Backend was not running"
    fi
}

# Stop frontend
stop_frontend() {
    print_info "Stopping frontend..."
    local stopped=0
    
    # Method 1: Kill via PID file
    if [ -f "$FRONTEND_PID_FILE" ]; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_info "Killing frontend process from PID file (PID: $pid)..."
            kill $pid 2>/dev/null || true
            stopped=1
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi

    # Method 2: Kill via Port 4142
    local port_pid=$(lsof -t -i:4142 -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$port_pid" ]; then
        for p in $port_pid; do
            print_info "Killing frontend process on port 4142 (PID: $p)..."
            kill -9 $p 2>/dev/null || true
            stopped=1
        done
    fi
    
    if [ $stopped -eq 1 ]; then
        # Wait for port to be free
        local retries=0
        while lsof -i:4142 -sTCP:LISTEN >/dev/null 2>&1; do
            sleep 0.5
            retries=$((retries+1))
            if [ $retries -gt 10 ]; then
                print_warning "Frontend port 4142 still in use after waiting. Forcing kill..."
                local stubborn_pid=$(lsof -t -i:4142 -sTCP:LISTEN 2>/dev/null || true)
                if [ -n "$stubborn_pid" ]; then
                    kill -9 $stubborn_pid 2>/dev/null || true
                fi
            fi
        done
        print_success "Frontend stopped"
    else
        print_warning "Frontend was not running"
    fi
}

# Show status
show_status() {
    print_header "Service Status"

    # Backend status
    if is_running "$BACKEND_PID_FILE"; then
        local pid=$(cat "$BACKEND_PID_FILE")
        print_success "Backend: Running (PID: $pid, URL: http://localhost:8000)"
    else
        print_warning "Backend: Stopped"
    fi

    # Frontend status
    if is_running "$FRONTEND_PID_FILE"; then
        local pid=$(cat "$FRONTEND_PID_FILE")
        print_success "Frontend: Running (PID: $pid, URL: http://localhost:4142)"
    else
        print_warning "Frontend: Stopped"
    fi

    echo ""
}

# Show logs
show_logs() {
    local service=$1

    case $service in
        backend)
            if [ -f "$BACKEND_LOG" ]; then
                print_header "Backend Logs (last 50 lines)"
                tail -n 50 "$BACKEND_LOG"
            else
                print_warning "No backend logs found"
            fi
            ;;
        frontend)
            if [ -f "$FRONTEND_LOG" ]; then
                print_header "Frontend Logs (last 50 lines)"
                tail -n 50 "$FRONTEND_LOG"
            else
                print_warning "No frontend logs found"
            fi
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Usage: $0 logs [backend|frontend]"
            exit 1
            ;;
    esac
}

# Follow logs
follow_logs() {
    local service=$1

    case $service in
        backend)
            if [ -f "$BACKEND_LOG" ]; then
                print_header "Following Backend Logs (Ctrl+C to stop)"
                tail -f "$BACKEND_LOG"
            else
                print_warning "No backend logs found"
            fi
            ;;
        frontend)
            if [ -f "$FRONTEND_LOG" ]; then
                print_header "Following Frontend Logs (Ctrl+C to stop)"
                tail -f "$FRONTEND_LOG"
            else
                print_warning "No frontend logs found"
            fi
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Usage: $0 follow [backend|frontend]"
            exit 1
            ;;
    esac
}

# Restart service
restart_service() {
    local service=$1

    case $service in
        backend)
            stop_backend
            sleep 1
            start_backend
            ;;
        frontend)
            stop_frontend
            sleep 1
            build_frontend
            start_frontend
            ;;
        all)
            stop_backend
            stop_frontend
            sleep 1
            start_backend
            build_frontend
            start_frontend
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Usage: $0 restart [backend|frontend|all]"
            exit 1
            ;;
    esac
}

# Run tests
run_tests() {
    local service=$1

    print_header "Running Tests"

    case $service in
        backend)
            if [ -d "$BACKEND_DIR" ]; then
                print_info "Running backend tests..."
                cd "$BACKEND_DIR"
                python3 -m pytest
                cd "$SCRIPT_DIR"
            else
                print_error "Backend directory not found"
            fi
            ;;
        frontend)
            if [ -d "$FRONTEND_DIR" ]; then
                print_info "Running frontend tests..."
                cd "$FRONTEND_DIR"
                npm test
                cd "$SCRIPT_DIR"
            else
                print_error "Frontend directory not found"
            fi
            ;;
        all)
            run_tests backend
            run_tests frontend
            ;;
        *)
            print_error "Unknown service: $service"
            print_info "Usage: $0 test [backend|frontend|all]"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    cat << EOF
oh-my-astock Management Script

Usage: $0 <command> [options]

Commands:
    start [service]          Start services (backend, frontend, or all)
    stop [service]           Stop services (backend, frontend, or all)
    restart [service]        Restart services (backend, frontend, or all) - rebuilds frontend
    build [service]          Build services (frontend or all)
    status                   Show status of all services
    logs <service>           Show logs for a service (backend or frontend)
    follow <service>         Follow logs for a service (backend or frontend)
    test [service]           Run tests (backend, frontend, or all)
    install                  Install dependencies for all services
    setup                    Setup environment files
    check                    Check dependencies
    help                     Show this help message

Examples:
    $0 start all             Start both backend and frontend
    $0 start backend         Start only backend
    $0 stop all              Stop both services
    $0 restart frontend      Restart frontend with rebuild
    $0 restart all           Restart all services with frontend rebuild
    $0 build frontend        Build frontend only
    $0 status                Show service status
    $0 logs backend          Show backend logs
    $0 follow frontend       Follow frontend logs in real-time
    $0 test all              Run all tests

Service URLs:
    Backend:  http://localhost:8000
    Frontend: http://localhost:4142

Log Files:
    Backend:  $BACKEND_LOG
    Frontend: $FRONTEND_LOG

EOF
}

# Main command handler
main() {
    case "${1:-}" in
        start)
            case "${2:-all}" in
                backend)
                    print_header "Starting Backend"
                    start_backend
                    ;;
                frontend)
                    print_header "Starting Frontend"
                    start_frontend
                    ;;
                all)
                    print_header "Starting All Services"
                    start_backend
                    start_frontend
                    echo ""
                    show_status
                    ;;
                *)
                    print_error "Unknown service: ${2}"
                    print_info "Usage: $0 start [backend|frontend|all]"
                    exit 1
                    ;;
            esac
            ;;
        stop)
            case "${2:-all}" in
                backend)
                    print_header "Stopping Backend"
                    stop_backend
                    ;;
                frontend)
                    print_header "Stopping Frontend"
                    stop_frontend
                    ;;
                all)
                    print_header "Stopping All Services"
                    stop_backend
                    stop_frontend
                    ;;
                *)
                    print_error "Unknown service: ${2}"
                    print_info "Usage: $0 stop [backend|frontend|all]"
                    exit 1
                    ;;
            esac
            ;;
        restart)
            print_header "Restarting Service"
            restart_service "${2:-all}"
            ;;
        status)
            show_status
            ;;
        logs)
            if [ -z "${2:-}" ]; then
                print_error "Service name required"
                print_info "Usage: $0 logs [backend|frontend]"
                exit 1
            fi
            show_logs "$2"
            ;;
        follow)
            if [ -z "${2:-}" ]; then
                print_error "Service name required"
                print_info "Usage: $0 follow [backend|frontend]"
                exit 1
            fi
            follow_logs "$2"
            ;;
        test)
            run_tests "${2:-all}"
            ;;
        build)
            case "${2:-all}" in
                frontend)
                    print_header "Building Frontend"
                    build_frontend
                    ;;
                all)
                    print_header "Building All Services"
                    build_frontend
                    ;;
                *)
                    print_error "Unknown service: ${2}"
                    print_info "Usage: $0 build [frontend|all]"
                    exit 1
                    ;;
            esac
            ;;
        install)
            check_dependencies
            install_deps
            print_success "Installation complete"
            ;;
        setup)
            setup_env
            print_success "Environment setup complete"
            ;;
        check)
            check_dependencies
            print_success "All dependencies are installed"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            if [ -n "${1:-}" ]; then
                print_error "Unknown command: ${1}"
                echo ""
            fi
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
