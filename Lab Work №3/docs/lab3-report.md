# Лабораторная работа №3
**Тема:** использование принципов проектирования на уровне методов и классов

**Цель работы:** получить опыт проектирования и реализации модулей с использованием принципов KISS, YAGNI, DRY, SOLID и др.

**Вариант использования:** преподаватель выставляет/редактирует оценку студенту по элементу контроля; система пересчитывает итог и пишет аудит

## Диаграмма контейнеров

![Диаграмма контейнеров](./container_diagram_1.png)

## Диаграмма компонентов

![Диаграмма компонентов](./component_diagram_1.png)

## Диаграмма последовательностей
![Диаграмма последовательностей](./usecase_diagram.png)

## Модель БД
![Модель БД](./database_model_uml.png)

## Применение основных принципов разработки
### KISS
KISS — решение должно быть максимально понятным и прямолинейным. 

**Серверный код:**
``` csharp
public static void ValidatePoints(decimal points, int maxPoints)
{
    if (points < 0 || points > maxPoints)
        throw new ArgumentOutOfRangeException(nameof(points), "Points out of range.");
}
```
В этом фрагменте вместо сложных правил и вложенных условий сделана одна очевидная проверка диапазона, которую легко прочитать, протестировать и переиспользовать в use case выставления оценки.

**Клиентский код:**
``` typescript
export function isPointsValid(points: number, maxPoints: number): boolean {
  return points >= 0 && points <= maxPoints;
}
```
Здесь проверка валидности баллов — это одна прозрачная функция без лишних условий и побочных эффектов, которую легко читать и использовать перед отправкой оценки на сервер.

### YAGNI
YAGNI — реализуем только то, что требуется текущему сценарию. 

**Серверный код:**
``` csharp
public sealed record UpsertGradeRequest(Guid StudentId, Guid AssessmentItemId, decimal Points);
```
Здесь контракт запроса содержит ровно три поля, необходимые для выставления/редактирования оценки; мы не добавляем заранее комментарии, причины изменения, вложения или сложные метаданные, пока бизнес реально их не потребовал.

**Клиентский код:**
``` typescript
export type UpsertGradeRequest = {
  studentId: string;
  assessmentItemId: string;
  points: number;
};
```
В этом контракте есть только поля, которые требуются для текущего сценария “выставить/редактировать оценку”; мы не добавляем заранее комментарии, вложения или сложные метаданные.

### DRY
DRY — одинаковую логику не нужно размножать по коду.

**Серверный код:**
``` csharp
public interface IGradeRepository
{
    Task UpsertGradeAsync(Guid gradebookId, Guid studentId, Guid assessmentItemId, decimal points, CancellationToken ct);
}
```
В этом фрагменте вместо двух методов CreateGrade и UpdateGrade используется один UpsertGradeAsync, который покрывает оба случая; благодаря этому не дублируется код сохранения и не возникает рассинхрон логики между “созданием” и “обновлением”.

**Клиентский код:**
``` typescript
export async function apiPost<TReq, TRes>(url: string, body: TReq): Promise<TRes> {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(body),
  });

  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return (await res.json()) as TRes;
}
```
Этот общий helper убирает дублирование fetch + headers + JSON.stringify + обработка ошибок по всем страницам, и дальше любой API-вызов делается в одну строку.

### SOLID
SOLID — набор принципов, которые делают код расширяемым и поддерживаемым. Ключевая идея — разделение ответственности и зависимости от абстракций. 

**Серверный код:**
``` csharp
public sealed class GradebookService
{
    private readonly IGradeRepository _repo;
    private readonly IEvaluationEngine _eval;

    public GradebookService(IGradeRepository repo, IEvaluationEngine eval)
    {
        _repo = repo;
        _eval = eval;
    }

    public async Task<GradeResultDto> UpsertAndRecalculateAsync(Guid gradebookId, UpsertGradeRequest req, CancellationToken ct)
    {
        await _repo.UpsertGradeAsync(gradebookId, req.StudentId, req.AssessmentItemId, req.Points, ct);
        var grades = await _repo.GetGradesForStudentAsync(gradebookId, req.StudentId, ct);
        return _eval.Recalculate(gradebookId, req.StudentId, grades);
    }
}
```
В этом фрагменте сервис не знает, как именно хранятся оценки (это скрыто за IGradeRepository), и не содержит алгоритм расчёта итогов (это IEvaluationEngine), поэтому реализацию репозитория или расчёта можно заменить без переписывания сервиса, а обязанности не смешиваются в одном классе.

**Клиентский код:**
``` typescript
export interface IGradeApi {
  upsertGrade(gradebookId: string, req: UpsertGradeRequest): Promise<GradeResultDto>;
}

export class GradeApi implements IGradeApi {
  async upsertGrade(gradebookId: string, req: UpsertGradeRequest): Promise<GradeResultDto> {
    return apiPost<UpsertGradeRequest, GradeResultDto>(`/api/gradebooks/${gradebookId}/grades`, req);
  }
}

export type GradeResultDto = { studentId: string; totalPoints: number; status: string };
```
Компоненты UI могут зависеть от интерфейса IGradeApi, а конкретную реализацию GradeApi можно заменить (например, на мок для тестов или на другую реализацию транспорта) без изменения UI-логики, потому что контракт остаётся тем же.

## Дополнительные принципы разработки
### BDUF
BDUF — это подход, при котором архитектуру и детали проектирования стараются максимально полно продумать заранее, до активной разработки. 

Для системы рабочих ведомостей BDUF не подходит, потому что в проекте высока вероятность изменений: могут уточниться интеграции (SSO/LMS/расписание), формат отчётов, правила расчёта оценок, роли и права. 

### SoC
SoC — принцип разделения ответственности: каждая часть системы отвечает за свою «зону», а не за всё сразу. 

Для нашего проекта он максимально применим, потому что система естественно делится на слои и модули: UI отдельно от Backend API, бизнес-логика отдельно от доступа к данным, расчёт итогов отдельно от CRUD-операций, аудит отдельно от основного сценария, отчётность вынесена в отдельный сервис. Такое разделение снижает связанность, упрощает тестирование и позволяет развивать разные части независимо (например, менять алгоритм оценивания или способ генерации XLSX без переписывания контроллеров).

### MVP
MVP — это минимально жизнеспособная версия продукта, которая уже решает ключевую проблему пользователя и позволяет получать обратную связь. 

Для веб-версии ведомостей это очень применимо: сначала достаточно реализовать ядро — авторизацию, список дисциплин/групп, ввод оценок и посещаемости, простой расчёт итогов, просмотр студентом своих результатов и базовую выгрузку. После появления работающего MVP можно добавлять улучшения: более гибкие формулы, расширенную отчётность, роли в учебном офисе, интеграции, массовые операции, уведомления. 

### PoC
PoC — небольшой эксперимент, который доказывает, что ключевая идея или технология реально работает в заданных условиях. 

Для проекта рабочих ведомостей PoC полезен точечно там, где есть технологические или организационные риски, например интеграция с SSO (какой протокол, какие токены, как получать роли), генерация XLSX (шаблоны, производительность, требования к формату), массовый ввод оценок и нагрузка в пиковые периоды, а также модель прав доступа и аудит. В этих местах PoC позволяет быстро подтвердить выбранный стек и подход, прежде чем вкладываться в полноценную реализацию и архитектурную обвязку.
