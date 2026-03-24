# Лабораторная работа №6
**Тема:** Использование шаблонов проектирования

**Цель работы:** Получить опыт применения шаблонов проектирования при написании кода программной системы.
## Шаблоны проектирования GoF
### Порождающие шаблоны

### Factory Method (Фабричный метод)

**Общее назначение:** шаблон Factory Method определяет общий интерфейс для создания объектов, но позволяет подклассам решать, объект какого конкретного класса необходимо создавать. Это уменьшает связанность между кодом клиента и конкретными реализациями создаваемых объектов.

**Назначение в рамках проекта**: в системе рабочих ведомостей шаблон удобно применить для экспорта отчетов. Пользователь или сотрудник учебного офиса может формировать отчет в разных форматах. При этом код бизнес-логики не должен зависеть от конкретного экспортера (`xlsx`, `сsv` и т.д.). Фабричный метод позволяет вынести создание конкретного экспортера в отдельные классы.

**UML-диаграмма**
![Factory Method](./factory_method.png)

**Пример кода**
```csharp
public class GradebookReport
{
    public Guid GradebookId { get; set; }
    public string Title { get; set; } = string.Empty;
    public byte[] Content { get; set; } = Array.Empty<byte>();
}

public interface IReportExporter
{
    byte[] Export(GradebookReport report);
}

public class XlsxReportExporter : IReportExporter
{
    public byte[] Export(GradebookReport report)
    {
        return System.Text.Encoding.UTF8.GetBytes($"XLSX report: {report.Title}");
    }
}

public class CsvReportExporter : IReportExporter
{
    public byte[] Export(GradebookReport report)
    {
        return System.Text.Encoding.UTF8.GetBytes($"CSV report: {report.Title}");
    }
}

public abstract class ReportExportService
{
    public byte[] ExportReport(GradebookReport report)
    {
        var exporter = CreateExporter();
        return exporter.Export(report);
    }
    protected abstract IReportExporter CreateExporter();
}

public class XlsxReportExportService : ReportExportService
{
    protected override IReportExporter CreateExporter()
    {
        return new XlsxReportExporter();
    }
}

public class CsvReportExportService : ReportExportService
{
    protected override IReportExporter CreateExporter()
    {
        return new CsvReportExporter();
    }
}
```

**Результат применения:** использование шаблона позволяет расширять список форматов экспорта без изменения общего алгоритма формирования отчета. Для добавления нового формата достаточно создать новый класс экспортера и соответствующий сервис.

### Abstract Factory (Абстрактная фабрика)

**Общее назначение:** шаблон Abstract Factory предоставляет интерфейс для создания семейств связанных объектов без указания их конкретных классов. Он полезен, когда в системе есть несколько наборов совместимых компонентов.

**Назначение в рамках проекта:** в системе рабочих ведомостей предусмотрены интеграции с внешними системами университета: SSO, LMS и системой расписания. Для разных сред выполнения (например, реальной и тестовой) могут использоваться разные реализации этих клиентов.  
Абстрактная фабрика позволяет создавать согласованный набор интеграционных адаптеров для выбранной среды.

**UML-диаграмма**
![Abstract Factory](./abstract_factory.png)

**Пример кода**
```csharp
public interface IAuthGateway
{
    Task<string> GetCurrentUserAsync(string token);
}

public interface ILmsGateway
{
    Task<IReadOnlyCollection<string>> GetCourseMaterialsAsync(Guid disciplineId);
}

public interface IScheduleGateway
{
    Task<IReadOnlyCollection<DateTime>> GetLessonDatesAsync(Guid groupId);
}

public interface IUniversityIntegrationFactory
{
    IAuthGateway CreateAuthGateway();
    ILmsGateway CreateLmsGateway();
    IScheduleGateway CreateScheduleGateway();
}

public class ProductionAuthGateway : IAuthGateway
{
    public Task<string> GetCurrentUserAsync(string token)
        => Task.FromResult("prod-user");
}

public class ProductionLmsGateway : ILmsGateway
{
    public Task<IReadOnlyCollection<string>> GetCourseMaterialsAsync(Guid disciplineId)
        => Task.FromResult<IReadOnlyCollection<string>>(new[] { "Lecture 1", "Lecture 2" });
}

public class ProductionScheduleGateway : IScheduleGateway
{
    public Task<IReadOnlyCollection<DateTime>> GetLessonDatesAsync(Guid groupId)
        => Task.FromResult<IReadOnlyCollection<DateTime>>(new[] { DateTime.Today, DateTime.Today.AddDays(7) });
}

public class StubAuthGateway : IAuthGateway
{
    public Task<string> GetCurrentUserAsync(string token)
        => Task.FromResult("stub-user");
}

public class StubLmsGateway : ILmsGateway
{
    public Task<IReadOnlyCollection<string>> GetCourseMaterialsAsync(Guid disciplineId)
        => Task.FromResult<IReadOnlyCollection<string>>(new[] { "Stub material" });
}

public class StubScheduleGateway : IScheduleGateway
{
    public Task<IReadOnlyCollection<DateTime>> GetLessonDatesAsync(Guid groupId)
        => Task.FromResult<IReadOnlyCollection<DateTime>>(new[] { DateTime.Today });
}

public class ProductionIntegrationFactory : IUniversityIntegrationFactory
{
    public IAuthGateway CreateAuthGateway() => new ProductionAuthGateway();
    public ILmsGateway CreateLmsGateway() => new ProductionLmsGateway();
    public IScheduleGateway CreateScheduleGateway() => new ProductionScheduleGateway();
}

public class StubIntegrationFactory : IUniversityIntegrationFactory
{
    public IAuthGateway CreateAuthGateway() => new StubAuthGateway();
    public ILmsGateway CreateLmsGateway() => new StubLmsGateway();
    public IScheduleGateway CreateScheduleGateway() => new StubScheduleGateway();
}

public class IntegrationSyncService
{
    private readonly IAuthGateway _authGateway;
    private readonly ILmsGateway _lmsGateway;
    private readonly IScheduleGateway _scheduleGateway;

    public IntegrationSyncService(IUniversityIntegrationFactory factory)
    {
        _authGateway = factory.CreateAuthGateway();
        _lmsGateway = factory.CreateLmsGateway();
        _scheduleGateway = factory.CreateScheduleGateway();
    }

    public async Task SyncAsync(Guid disciplineId, Guid groupId, string token)
    {
        var user = await _authGateway.GetCurrentUserAsync(token);
        var materials = await _lmsGateway.GetCourseMaterialsAsync(disciplineId);
        var dates = await _scheduleGateway.GetLessonDatesAsync(groupId);

        Console.WriteLine($"{user}: {materials.Count} materials, {dates.Count} dates");
    }
}
```

**Результат применения:** шаблон позволяет переключаться между наборами интеграций без изменения кода сервиса синхронизации. Это особенно полезно для тестирования, локальной разработки и подключения реальных внешних сервисов в продуктивной среде.

### Builder (Строитель)

**Общее назначение:** шаблон Builder позволяет создавать сложный объект поэтапно, отделяя процесс конструирования от итогового представления. Это полезно, когда объект имеет много частей и опциональных блоков.

**Назначение в рамках проекта:** в системе рабочих ведомостей можно формировать сложный отчет по дисциплине, который включает различные разделы: общие сведения, оценки, посещаемость, статистику. Не всегда нужно включать все части сразу. Шаблон Builder позволяет пошагово собирать такой объект отчета и получать разные варианты результата при одном процессе построения.

**UML-диаграмма**
![Builder](./builder.png)

**Пример кода**
```csharp
public class GradebookReportDto
{
    public string Header { get; set; } = string.Empty;
    public List<string> Grades { get; set; } = new();
    public List<string> Attendance { get; set; } = new();
    public string Statistics { get; set; } = string.Empty;
}

public interface IGradebookReportBuilder
{
    void Reset();
    void BuildHeader(string disciplineName, string groupName);
    void BuildGrades(IEnumerable<string> grades);
    void BuildAttendance(IEnumerable<string> attendance);
    void BuildStatistics(string statistics);
    GradebookReportDto GetResult();
}

public class GradebookReportBuilder : IGradebookReportBuilder
{
    private GradebookReportDto _report = new();

    public void Reset()
    {
        _report = new GradebookReportDto();
    }

    public void BuildHeader(string disciplineName, string groupName)
    {
        _report.Header = $"Discipline: {disciplineName}; Group: {groupName}";
    }

    public void BuildGrades(IEnumerable<string> grades)
    {
        _report.Grades.AddRange(grades);
    }

    public void BuildAttendance(IEnumerable<string> attendance)
    {
        _report.Attendance.AddRange(attendance);
    }

    public void BuildStatistics(string statistics)
    {
        _report.Statistics = statistics;
    }

    public GradebookReportDto GetResult()
    {
        return _report;
    }
}

public class GradebookReportDirector
{
    private readonly IGradebookReportBuilder _builder;

    public GradebookReportDirector(IGradebookReportBuilder builder)
    {
        _builder = builder;
    }

    public GradebookReportDto BuildFullReport()
    {
        _builder.Reset();
        _builder.BuildHeader("Архитектура программных систем", "РИС-22-3");
        _builder.BuildGrades(new[] { "Иванов - 8", "Петрова - 9" });
        _builder.BuildAttendance(new[] { "Иванов - 90%", "Петрова - 100%" });
        _builder.BuildStatistics("Средний балл: 8.5");
        return _builder.GetResult();
    }
}
```

**Результат применения:** шаблон Builder делает построение сложного объекта отчета управляемым и расширяемым. Можно легко создавать разные типы отчетов: полный, краткий, только по оценкам, только по посещаемости и т.д.

### Структурные шаблоны
<Представить с пояснения по каждому шаблону, указав: название, общее назначение и назначение согласно реализуемому функционалу, сопроводив UML-диаграммой и соответствующим фрагментом программного кода>

### Поведенческие шаблоны
<Представить с пояснения по каждому шаблону, указав: название, общее назначение и назначение согласно реализуемому функционалу, сопроводив UML-диаграммой и соответствующим фрагментом программного кода>
