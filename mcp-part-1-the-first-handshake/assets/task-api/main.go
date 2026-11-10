package main

import (
	"encoding/json"
	"log"
	"net/http"
	"strconv"
	"strings"
	"sync"
	"time"
)

// Task represents a todo item in our task manager.
type Task struct {
	ID        int       `json:"id"`
	Title     string    `json:"title"`
	Status    string    `json:"status"` // "PENDING" or "COMPLETED"
	CreatedAt time.Time `json:"created_at"`
}

// TaskStore manages concurrent in-memory storage for tasks.
type TaskStore struct {
	mu     sync.RWMutex
	tasks  []Task
	nextID int
}

func NewTaskStore() *TaskStore {
	return &TaskStore{
		tasks:  make([]Task, 0),
		nextID: 1,
	}
}

// AddTask adds a new task with "PENDING" status and returns the created task.
func (s *TaskStore) AddTask(title string) Task {
	s.mu.Lock()
	defer s.mu.Unlock()

	task := Task{
		ID:        s.nextID,
		Title:     title,
		Status:    "PENDING",
		CreatedAt: time.Now().UTC(),
	}
	s.nextID++
	s.tasks = append(s.tasks, task)
	return task
}

// ListTasks returns tasks optionally filtered by status ("ALL", "PENDING", "COMPLETED").
func (s *TaskStore) ListTasks(filterStatus string) []Task {
	s.mu.RLock()
	defer s.mu.RUnlock()

	filter := strings.ToUpper(strings.TrimSpace(filterStatus))
	if filter == "" || filter == "ALL" {
		out := make([]Task, len(s.tasks))
		copy(out, s.tasks)
		return out
	}

	var filtered []Task
	for _, task := range s.tasks {
		if strings.EqualFold(task.Status, filter) {
			filtered = append(filtered, task)
		}
	}
	if filtered == nil {
		return []Task{}
	}
	return filtered
}

// CompleteTask marks a task as "COMPLETED" by ID. Returns true if found and updated.
func (s *TaskStore) CompleteTask(id int) (Task, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()

	for i := range s.tasks {
		if s.tasks[i].ID == id {
			s.tasks[i].Status = "COMPLETED"
			return s.tasks[i], true
		}
	}
	return Task{}, false
}

// Server wires the HTTP handlers to the TaskStore.
type Server struct {
	store *TaskStore
}

func NewServer(store *TaskStore) *Server {
	return &Server{store: store}
}

func (srv *Server) HandleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"ok"}`))
}

func (srv *Server) HandleTasks(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	switch r.Method {
	case http.MethodGet:
		status := r.URL.Query().Get("status")
		tasks := srv.store.ListTasks(status)
		if tasks == nil {
			tasks = []Task{}
		}
		json.NewEncoder(w).Encode(tasks)

	case http.MethodPost:
		var req struct {
			Title string `json:"title"`
		}
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil || strings.TrimSpace(req.Title) == "" {
			http.Error(w, `{"error":"invalid title"}`, http.StatusBadRequest)
			return
		}
		task := srv.store.AddTask(strings.TrimSpace(req.Title))
		w.WriteHeader(http.StatusCreated)
		json.NewEncoder(w).Encode(task)

	default:
		http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
	}
}

func (srv *Server) HandleCompleteTask(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	if r.Method != http.MethodPut && r.Method != http.MethodPost {
		http.Error(w, `{"error":"method not allowed"}`, http.StatusMethodNotAllowed)
		return
	}

	// Path: /tasks/{id}/complete
	parts := strings.Split(strings.Trim(r.URL.Path, "/"), "/")
	if len(parts) < 3 || parts[0] != "tasks" || parts[2] != "complete" {
		http.Error(w, `{"error":"invalid path"}`, http.StatusBadRequest)
		return
	}

	id, err := strconv.Atoi(parts[1])
	if err != nil {
		http.Error(w, `{"error":"invalid id"}`, http.StatusBadRequest)
		return
	}

	task, ok := srv.store.CompleteTask(id)
	if !ok {
		http.Error(w, `{"error":"task not found"}`, http.StatusNotFound)
		return
	}

	json.NewEncoder(w).Encode(task)
}

func main() {
	store := NewTaskStore()
	srv := NewServer(store)

	mux := http.NewServeMux()
	mux.HandleFunc("/health", srv.HandleHealth)
	mux.HandleFunc("/tasks", srv.HandleTasks)
	mux.HandleFunc("/tasks/", srv.HandleCompleteTask)

	port := ":8080"
	log.Printf("Starting Task REST API on http://localhost%s ...", port)
	if err := http.ListenAndServe(port, mux); err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
